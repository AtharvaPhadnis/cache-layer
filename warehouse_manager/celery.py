import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warehouse_manager.settings')

app = Celery('warehouse_manager')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.requst!r}')

