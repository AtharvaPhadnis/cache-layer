from django.urls import path
from . import views  # This works because urls.py and views.py are in the same app

urlpatterns = [
    path('', views.say_hello, name='say_hello'),
]