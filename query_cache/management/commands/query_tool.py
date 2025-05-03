import time
import hashlib
import json
import redis
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Executes SQL queries with Redis caching'

    def add_arguments(self, parser):
        parser.add_argument('sql', type=str, help='SQL query to execute')

    def handle(self, *args, **options):
        sql = options['sql']
        
        start_time = time.time()
        
        # Use sha for now
        hash_key = hashlib.sha224(sql.encode()).hexdigest()
        redis_key = f"sql_cache:{hash_key}"
        
        r = redis.Redis(host='redis', port=6379, db=0)
        
        cached_result = r.get(redis_key)
        
        if cached_result:
            # Cache hit
            self.stdout.write(self.style.SUCCESS("Cache Hit!"))
            result = json.loads(cached_result)
        else:
            # Cache miss
            with connection.cursor() as cursor:
                cursor.execute(sql)
                columns = [col[0] for col in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # TTL : 1hr for now...
            r.set(redis_key, json.dumps(result, default=str), ex=3600)
        
        elapsed_time = time.time() - start_time
        
        self.stdout.write(json.dumps(result, indent=2, default=str))
        self.stdout.write(f"Query executed in {elapsed_time:.4f} seconds")
