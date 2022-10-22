from django.shortcuts import render
from app.models import FailedEntries
from app.filters import FailedEntriesFilter
import re
import json
from json import JSONDecodeError


def failed_entries(request, dag_id, run_id):
    failed_entries = FailedEntries.objects.filter(dag_id=dag_id, run_id=run_id).order_by('created_at')
    failed_entries_filter = FailedEntriesFilter(request.GET, queryset=failed_entries)
    failed_entries = failed_entries_filter.qs

    failed_entries_context = {}
    for failed_entry in failed_entries:
        if failed_entry.job_id not in failed_entries_context:
            failed_entries_context[failed_entry.job_id] = []

        # Fix old incorrect single quotes dicts in failed_entries.input and failed_entries.data
        p = re.compile('(?<!\\\\)\'')
        try:
            failed_entry_data = json.loads(p.sub('\"', failed_entry.data))
            failed_entry_input = json.loads(failed_entry.input)
        except JSONDecodeError:
            failed_entry_data = failed_entry.data
            failed_entry_input = json.loads(failed_entry.input)

        failed_entries_context[failed_entry.job_id].append({
            'task_id': failed_entry.task_id,
            'input': failed_entry_input,
            'data': failed_entry_data,
            'info': failed_entry.info,
        })

    context = {'failed_entries': failed_entries_context, 'failed_entries_filter': failed_entries_filter, 'args': [dag_id, run_id]}

    return render(request, 'app/failed_entries.html', context)
