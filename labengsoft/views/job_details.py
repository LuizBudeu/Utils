from django.shortcuts import render
from app.models import JobDetails
from app.filters import JobDetailsFilter
import json
import re


def job_details(request, dag_id, run_id, code):
    job_details = JobDetails.objects.filter(dag_id=dag_id, run_id=run_id, code=code).order_by('job_id')
    job_details_filter = JobDetailsFilter(request.GET, queryset=job_details)
    job_details = job_details_filter.qs

    job_details_context = {}
    for job_detail in job_details:
        if job_detail.job_id not in job_details_context:
            job_details_context[job_detail.job_id] = []

        # Fix old incorrect single quotes dicts in job_details.input
        p = re.compile('(?<!\\\\)\'')
        job_detail_input = p.sub('\"', job_detail.input)

        job_details_context[job_detail.job_id].append({
            'task_id': job_detail.task_id,
            'input': json.loads(job_detail_input),
        })

    context = {
        'job_details': job_details_context,
        'job_details_filter': job_details_filter,
        'args': {
            'dag_id': dag_id, 'run_id': run_id, 'code': code
        }
    }

    return render(request, 'app/job_details.html', context)
