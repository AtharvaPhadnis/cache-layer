from django.urls import path
from .views import SQLQueryView, CSVExportView, DownloadView, TaskStatusView 

app_name = "query_api"

urlpatterns = [
    path('v1/sql', SQLQueryView.as_view(), name='sql_query'),
    path('v1/csv', CSVExportView.as_view(), name='csv_export'),
    path('v1/csv/download/<str:filename>/', DownloadView.as_view(), name='download'),
    path('v1/csv/status/<str:filename>/', TaskStatusView.as_view(), name='status'),
]