from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-email-contract-notice-day': {
        'task': 'api.v1.contracts.tasks.send_beat_email',
        'schedule': crontab(minute='*/2'),
    },
    'send-email-fixed-terms': {
            'task': 'api.v1.contracts.tasks.check_fixed_terms',
            'schedule': crontab(minute='*/2'),
    },
    'send-email-renew-terms': {
            'task': 'api.v1.contracts.tasks.check_auto_renew_terms',
            'schedule': crontab(minute='*/2'),
    },
    'auto-create-service-pay-terms': {
            'task': 'api.v1.services.tasks.auto_create_increase_terms',
            'schedule': crontab(minute='*/2'),
    },
    'check-organization-service-commodity-consultant-status': {
            'task': 'api.v1.services.tasks.check_organization_service_commodity_consultant_status',
            'schedule': crontab(minute='*/2'),
    },
}

