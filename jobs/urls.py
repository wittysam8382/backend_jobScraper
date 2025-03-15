from django.urls import path
from .views import job_list, search_jobs

urlpatterns = [
    path('api/jobs/', job_list, name='job-list'),  # Returns all jobs
    path('api/search_jobs/', search_jobs, name='search_jobs'),  # Search by job title
]