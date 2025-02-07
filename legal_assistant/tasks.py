# Standard Python imports
import logging as logger
from datetime import datetime


from celery import shared_task
import time
import random
from django.core.mail import send_mail
from django.conf import settings
import openai
import faiss
import numpy as np
from langchain_community.embeddings import OpenAIEmbeddings
from .models import QueryJob, LegalDocument
from .index import index

@shared_task(bind=True, retry_backoff=True)
def process_query(self, job_id):
    try:
        job = QueryJob.objects.get(id=job_id)
        job.status = 'processing'
        job.save(update_fields=['status'])
        
        # Your existing FAISS search code
        embed_model = OpenAIEmbeddings()
        query_embedding = embed_model.embed_query(job.query)
        query_embedding = np.array(query_embedding).astype("float32").reshape(1, -1)
        _, I = index.search(query_embedding, k=3)
        relevant_docs = LegalDocument.objects.filter(id__in=I[0])
        retrieved_texts = "\n".join([doc.content for doc in relevant_docs])
        
        openai.api_key = settings.OPENAI_API_KEY
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a legal assistant."},
                {"role": "user", "content": f"{job.query}\n\nRelevant information:\n{retrieved_texts}"},
            ],
        )
        
        job.status = 'completed'
        job.result = response["choices"][0]["message"]["content"]
        job.completed_at = datetime.now()
        job.save(update_fields=['status', 'result', 'completed_at'])
        
        return response
        
    except openai.error.RateLimitError as e:
        raise self.retry(countdown=self.request.retries * 30)
    except Exception as e:
        job.status = 'failed'
        job.result = f"Error: {str(e)}"
        job.save(update_fields=['status', 'result'])
        logger.error(f"Query processing failed for job {job_id}: {str(e)}")
        raise


from celery import shared_task

@shared_task
def my_task():
    print("Celery task executed!")
    return "Task completed!"