import django_filters
from django_filters import DateFilter, CharFilter, IsoDateTimeFilter
from .models import FailedEntries
from .models import JobDetails
import datetime
from django import forms


class FailedEntriesFilter(django_filters.FilterSet):
    task_id = CharFilter(field_name='task_id', lookup_expr='icontains')

    class Meta:
        model = FailedEntries
        fields = ['job_id']

class JobsFilter(django_filters.FilterSet):
    dag_id = CharFilter(field_name='dag_id', lookup_expr='icontains')
    start_date = DateFilter(field_name='created_at', lookup_expr='gte', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    end_date = DateFilter(field_name='created_at', lookup_expr='lt', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    def __init__(self, data, *args, **kwargs):
        if not data.get('start_date'):
            data = data.copy()
            data['start_date'] = datetime.date.today()

        if not data.get('end_date'):
            data = data.copy()
            data['end_date'] = datetime.date.today() + datetime.timedelta(1)
        super().__init__(data, *args, **kwargs)

    class Meta:
        model = JobDetails
        fields = ['code', 'run_id']

class JobDetailsFilter(django_filters.FilterSet):
    task_id = CharFilter(field_name='task_id', lookup_expr='icontains')

    class Meta:
        model = JobDetails
        fields = ['job_id']

