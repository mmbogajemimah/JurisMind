from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import QueryJob
from .tasks import process_query

@api_view(["GET", "POST"])
def chatbot_response(request):
    if request.method == "GET":
        return JsonResponse({"message": "Use POST to send queries."}, status=200)
    
    user_query = request.data.get("query", "")
    if not user_query:
        return JsonResponse({"error": "Query is required"}, status=400)
    
    job = QueryJob.objects.create(
        query=user_query,
        status='pending'
    )
    
    process_query.delay(job.id)
    
    return JsonResponse({
        "job_id": str(job.id),
        "message": "Query received and queued for processing"
    })

@api_view(["GET"])
def check_job_status(request, job_id):
    try:
        job = QueryJob.objects.get(id=job_id)
        return JsonResponse({
            "status": job.status,
            "result": job.result,
            "created_at": job.created_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        })
    except QueryJob.DoesNotExist:
        return JsonResponse({"error": "Job not found"}, status=404)