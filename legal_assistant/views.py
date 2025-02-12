# views.py
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import QueryJob
from .tasks import process_query
from django.utils import timezone
from datetime import timedelta
from legal_assistant.logger_config import logger

def calculate_progress(job):
    """Calculate processing progress percentage"""
    if not job.created_at or not job.completed_at:
        return 0
    total_time = (timezone.now() - job.created_at).total_seconds()
    elapsed_time = (job.completed_at or timezone.now() - job.created_at).total_seconds()
    return min(int((elapsed_time / max(total_time, 1)) * 100), 100)

def estimate_completion(job):
    """Estimate remaining processing time"""
    if not job.created_at or not job.completed_at:
        return None
    total_time = (job.completed_at - job.created_at).total_seconds()
    current_elapsed = (timezone.now() - job.created_at).total_seconds()
    remaining = max(0, total_time - current_elapsed)
    return int(remaining) if remaining > 0 else 0

@api_view(['GET', 'POST'])
def chatbot_response(request):
    if request.method == 'GET':
        return JsonResponse({'message': 'Use POST to send queries.'}, status=200)
    
    user_query = request.data.get('query', '')
    if not user_query:
        return JsonResponse({'error': 'Query is required'}, status=400)
    
    try:
        job = QueryJob.objects.create(
            query=user_query,
            status='pending',
            created_at=timezone.now()
        )
        
        # Trigger async processing
        process_query.apply_async(args=[str(job.id)], retry_backoff=True)
        
        return JsonResponse({
            'job_id': str(job.id),
            'message': 'Query received and queued for processing',
            'status_url': request.build_absolute_uri(f'/jobs/{job.id}/status/')
        })
        
    except Exception as e:
        logger.error(f"Failed to create query job: {str(e)}")
        return JsonResponse({
            'error': 'Internal Server Error',
            'details': str(e)
        }, status=500)


from django.shortcuts import get_object_or_404

@api_view(['GET'])
def check_job_status(request, job_id):
    try:
        # Fetch QueryJob without select_related since 'result' is a JSONField
        job = get_object_or_404(QueryJob, id=job_id)
        
        return JsonResponse({
            "job_id": str(job.id),
            "query": job.query,
            "status": job.status,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "result": job.result,  # No need for hasattr check, since JSONField allows None
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)