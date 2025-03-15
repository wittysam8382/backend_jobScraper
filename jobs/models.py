from django.db import models

# Create your models here.
from django.db import models

class Job(models.Model):
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    rating = models.CharField(max_length=10, null=True, blank=True)
    experience = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=255)
    application_link = models.URLField()
    all_tech_stack = models.TextField()

    def __str__(self):
        return f"{self.title} at {self.company}"
