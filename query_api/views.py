from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from rest_framework.permissions import AllowAny
import time
import hashlib
import json
import redis


# Create your views here.
class SQLQueryView(APIView):
    permission_classes = [AllowAny] 

    def get(self, request):
        sql = request.GET.get('query')
        if not sql:
            return Response({'error': 'No SQL query provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cache_hit = False
            start_time = time.time()
            hash_key = hashlib.md5(sql.encode()).hexdigest()
            redis_key = f'sql_cache:{hash_key}'

            r = redis.Redis(host='redis', port=6379, db=0)

            cached_result = r.get(redis_key)
            
            if cached_result:
                cache_hit = True
                results = json.loads(cached_result)
                columns = list(results[0].keys()) if results else []
            
            else:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    columns = [col[0] for col in cursor.description] if cursor.description else []
                    rows = cursor.fetchall() if cursor.description else []
                    results = [dict(zip(columns, row)) for row in rows]

                r.set(redis_key, json.dumps(results, default=str), ex=3600)

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
            return Response({'query': sql, 'file': 'file', 'task_id': 1234})
        
        except Exception as e:
            return Response({'query': sql, 'error': str(e)}, status=status.HTTP_200_OK)



def dummy_api(request):
    return HttpResponse('This is an API endpoint', status=200)

