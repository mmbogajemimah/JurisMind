from django.urls import path
from .views import chatbot_response, check_job_status

urlpatterns = [
    path("chat/", chatbot_response, name="chatbot_response"),
    path("jobs/<uuid:job_id>/status/", check_job_status, name='job_status'),
]
