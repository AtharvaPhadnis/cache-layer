from django.db import connection
import hashlib
import json
import redis


def check_cache(sql):
    cache_hit = False
    hash_key = hashlib.md5(sql.encode()).hexdigest()
    redis_key = f'sql_cache:{hash_key}'

    r = redis.Redis(host='redis', port=6379, db=0)

    cached_result = r.get(redis_key)
    
    if cached_result:
        cache_hit = True
        results = json.loads(cached_result)
    
    else:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description] if cursor.description else []
            rows = cursor.fetchall() if cursor.description else []
            results = [dict(zip(columns, row)) for row in rows]

        r.set(redis_key, json.dumps(results, default=str), ex=3600)

    return results, cache_hit