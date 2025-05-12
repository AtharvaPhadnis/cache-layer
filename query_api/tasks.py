import csv
import os
import uuid
from celery import shared_task
from django.conf import settings
from django.db import connection
from .cache import check_cache


@shared_task
def export_to_csv_task(sql, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    results, cache_hit = check_cache(sql)
    columns = list(results[0].keys()) if results else []
    rows = [[res[col] for col in columns] for res in results]

    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    
    return filename





