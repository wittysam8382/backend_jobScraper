from datetime import time
import os
import subprocess
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Job
from .serializers import JobSerializer

@api_view(['GET'])  # Ensure it works with Django REST Framework
def search_jobs(request):
    job_title = request.GET.get('job_title', '').strip()

    if not job_title:
        return Response({"error": "Job title is required"}, status=400)

    # Check if jobs exist in the database
    jobs = Job.objects.filter(job_title__icontains=job_title)

    if not jobs.exists():
        
        try:
            # If not found, trigger the scraper

            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "working.py"))
            # Debug: Print script path
            print(f"Running script at: {script_path}")
            result = subprocess.run(["python", script_path, job_title], capture_output=True, text=True)
            print(result.stdout)  # Debugging: Print the script output
            print(result.stderr)  # Debugging: Print the script error output
            if result.returncode != 0:
                return Response({"error": "Scraping failed"}, status=500)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    

        # Fetch again after inserting new jobs
        jobs = Job.objects.filter(job_title__icontains=job_title)
        max_retries = 5
        retry_count = 0
        while retry_count < max_retries:
            jobs = Job.objects.filter(job_title__icontains=job_title)
            if jobs.exists():
                break
            time.sleep(2)
            retry_count += 1

    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)
@api_view(["GET"])
@api_view(["GET"])
def job_list(request):
    jobs = Job.objects.all()
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)