from django.shortcuts import render
from django.http import HttpResponse

def say_hello(request):
    return HttpResponse(f'Hello from {request.path_info}', status=200)

# Create your views here.
