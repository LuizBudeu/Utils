from django.shortcuts import render
from django.db.models import Sum, Count, Min
from app.models import JobDetails
from app.filters import JobsFilter
from app.services import JobResponse

# from typing import List, Optional
from airflow.models.taskinstance import TaskInstance
# from airflow.utils import State
# from airflow.settings import Session
from airflow.utils.db import provide_session
import datetime
import pytz
from sqlalchemy import tuple_
from app.services.base import Base


# View func
def jobs(request):
    start_date, end_date = get_dates(request)

    job_details_qs = JobDetails.objects.values('code', 'dag_id', 'run_id', 'task_id') \
        .annotate(failed_entries=Sum('failed_entries')) \
        .annotate(jobs=Count('*')) \
        .annotate(created_at=Min('created_at')) \
        .order_by()

    # Filter update
    jobs_filter = JobsFilter(request.GET, queryset=job_details_qs)
    job_details_qs = jobs_filter.qs

    job_details = get_job_details(job_details_qs)

    keys = ['code', 'dag_id', 'run_id']
    job_details_qs = Base.group_by_keys_and_aggregate(job_details_qs, keys, {'created_at': 'min', 'jobs': 'sum', 'failed_entries': 'sum'})

    jobs = {}
    for job_detail in job_details_qs:
        code = job_detail['code']
        dag_id = job_detail['dag_id']
        run_id = job_detail['run_id']

        if code not in jobs:
            jobs[code] = {}

        if dag_id not in jobs[code]:
            jobs[code][dag_id] = {}

        if run_id not in jobs[code][dag_id]:
            jobs[code][dag_id][run_id] = {}

        jobs[code][dag_id][run_id] = {
            'created_at': job_detail['created_at'],
            'jobs': job_detail['jobs'],
            'failed_entries': job_detail['failed_entries'],
            'title': JobResponse.REVERSE_CONFIG.get(code),
        }

    # Sort based on code, dag_id and created_at
    sort_jobs = sorted(jobs.items(), key=lambda x: x[0], reverse=True)
    jobs = dict(sort_jobs)

    for code in jobs:
        sort_dag_ids = sorted(jobs[code].items(), key=lambda x: x[0].lower())
        jobs[code] = dict(sort_dag_ids)

    # Colors
    colors = ["#a0fab5", "#f8fa8c", "#fa9993"]


    # Airflow failed before executes
    task_instances = get_task_instances(start_date, end_date, job_details)

    context = {
        'jobs': jobs,
        'jobs_filter': jobs_filter,
        'colors': colors,
        'failed_before_execute': {
            'list': task_instances,
            'start_date': start_date.strftime('%d-%m-%Y'),
            'end_date': end_date.strftime('%d-%m-%Y'),
        },
    }

    return render(request, 'app/jobs.html', context)


# Extras funcs
@provide_session
def get_task_instances(start_date, end_date, job_details, session=None):
    task_instances = session.query(TaskInstance) \
        .filter(
            TaskInstance.start_date >= start_date,
            TaskInstance.end_date <= end_date,
            TaskInstance.dag_id.contains('process'),
            TaskInstance.task_id != 'wait-prepare-tasks',
            TaskInstance.state != 'skipped',
            TaskInstance.state != 'upstream_failed',
            tuple_(TaskInstance.dag_id, TaskInstance.run_id, TaskInstance.task_id).notin_(job_details),
        ).all()

    task_instances_infos = []
    for task_instance in task_instances:
        task_instances_infos.append({
            'dag_id': task_instance.dag_id,
            'run_id': task_instance.run_id,
            'task_id': task_instance.task_id,
        })
    return task_instances


def get_job_details(job_details_qs):
    # job_details_qs = JobDetails.objects.filter(created_at__gte=start_date, created_at__lt=end_date).values('dag_id', 'run_id', 'task_id')

    job_details = []
    for job_detail in job_details_qs:
        job_details.append([job_detail['dag_id'], job_detail['run_id'], job_detail['task_id']])
    return job_details


def get_dates(request):
    start_date = request.GET.get('start_date', '')
    if not start_date:
        start_date = datetime.datetime.now(datetime.timezone.utc)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)

    end_date = request.GET.get('end_date', '')
    if not end_date:
        end_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(1)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)

    return start_date, end_date
