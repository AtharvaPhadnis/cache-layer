from django.urls import path
from .views import SQLQueryView, CSVExportView 

urlpatterns = [
    path('v1/sql', SQLQueryView.as_view(), name='sql_query'),
    path('v1/csv', CSVExportView.as_view(), name='csv_export'),
]