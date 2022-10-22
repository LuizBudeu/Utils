from django.urls import path, include
from . import views

urlpatterns = [
    path(r'jobs/', views.jobs, name='jobs'),
    path(r'failed_entries/<dag_id>/<run_id>/', views.failed_entries, name='failed_entries'),
    path(r'job_details/<dag_id>/<run_id>/<code>/', views.job_details, name='job_details')
]
