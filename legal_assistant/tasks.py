# tasks.py
import logging as logger
from datetime import datetime
import time
import random
import numpy as np
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from openai import OpenAIError
import openai
import faiss
from langchain_community.embeddings import OpenAIEmbeddings
from .models import QueryJob, LegalDocument
from .index import index
from functools import wraps

def retry_on_failure(max_retries=3, backoff_factor=2):
    """Decorator for automatic task retries"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Task {func.__name__} failed (attempt {retries + 1}/{max_retries}): {str(e)}")
                    if retries == max_retries:
                        raise
                    delay = backoff_factor * (2 ** retries)
                    time.sleep(delay)
                    retries += 1
        return wrapper
    return decorator

@shared_task(bind=True, retry_backoff=True)
def process_query(self, job_id):
    """Process a legal query asynchronously"""
    try:
        # Initialize job tracking
        job = QueryJob.objects.get(id=job_id)
        job.status = 'processing'
        job.save(update_fields=['status'])
        
        # Initialize embedding model with connection pooling
        embed_model = OpenAIEmbeddings()
        query_embedding = embed_model.embed_query(job.query)
        query_embedding = np.array(query_embedding).astype("float32").reshape(1, -1)
        
        # Search FAISS index with timeout handling
        _, I = index.search(query_embedding, k=3)
        
        # Retrieve relevant documents efficiently
        relevant_docs = LegalDocument.objects.filter(id__in=I[0])
        retrieved_texts = "\n".join([doc.content for doc in relevant_docs])
        
        # Configure OpenAI API with error handling
        openai.api_key = settings.OPENAI_API_KEY
        
        # Generate response with context
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a legal assistant."},
                {"role": "user", "content": f"{job.query}\n\nRelevant information:\n{retrieved_texts}"}
            ],
            timeout=30  # Add timeout for API calls
        )
        
        # Update job status and result
        job.status = 'completed'
        job.result = {
            'response': response['choices'][0]['message']['content'],
            'context': retrieved_texts,
            'relevant_documents': [{'id': doc.id, 'title': doc.title} for doc in relevant_docs]
        }
        job.completed_at = datetime.now()
        job.save(update_fields=['status', 'result', 'completed_at'])
        
        return response
        
    except OpenAIError as e:
        logger.warning(f"OpenAI rate limit error: {e}. Retrying...")
        raise self.retry(exc=e, countdown=min(30 * (self.request.retries + 1), 900))
        
    except Exception as e:
        job.status = 'failed'
        job.result = {
            'error': str(e),
            'error_type': type(e).__name__,
            'timestamp': datetime.now().isoformat(),
            'traceback': str(e.__traceback__)
        }
        job.save(update_fields=['status', 'result'])
        logger.error(f"Query processing failed for job {job_id}: {str(e)}")
        raise