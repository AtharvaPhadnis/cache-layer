from django.shortcuts import render
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from rest_framework.permissions import AllowAny
import time
import os
import hashlib
import json
import redis
import uuid
from .tasks import export_to_csv_task
from django.urls import reverse
from .cache import check_cache
from celery.result import AsyncResult



# Create your views here.
class SQLQueryView(APIView):
    permission_classes = [AllowAny] 

    def get(self, request):
        sql = request.GET.get('query')
        if not sql:
            return Response({'error': 'No SQL query provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_time = time.time()
            results, cache_hit = check_cache(sql)
            columns = list(results[0].keys()) if results else []

            elapsed_time = time.time() - start_time
            return Response({'cache hit': cache_hit, 'query exec time': elapsed_time, 'columns': columns, 'rows': results})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CSVExportView(APIView):
    permission_classes = [AllowAny] 
    def get(self, request):
        sql = request.GET.get('query')
        if not sql:
            return Response({'error': 'No SQL query provided.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Create celery task and return OK
            filename =f'{uuid.uuid4()}.csv'
            task = export_to_csv_task.delay(sql, filename)

            download_url = request.build_absolute_uri(
                reverse('query_api:download', args=[filename])
            )

            return Response({'query': sql, 
                            'task_id': task.id,
                            'status': 'PENDING',
                            'download_url': download_url})
        
        except Exception as e:
            return Response({'query': sql,
                            'task_id': -1,
                            'error': str(e)},
                            status=status.HTTP_200_OK)

class DownloadView(APIView):
    def get(self, request, filename):
        file_path = os.path.join(settings.MEDIA_ROOT, 'exports', filename)
        if not os.path.exists(file_path):
            raise Http404("File not ready")
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)

class TaskStatusView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id)
        return Response({'task_id': task_id, 'status': result.status})

def dummy_api(request):
    return HttpResponse('This is an API endpoint', status=200)

