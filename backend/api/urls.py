from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.PingView.as_view(), name='ping'),
    path('upload/', views.UploadCSVView.as_view(), name='upload'),
    path('datasets/', views.DatasetListView.as_view(), name='datasets'),
    path('datasets/<int:pk>/', views.DatasetDetailView.as_view(), name='dataset-detail'),
    path('datasets/<int:pk>/report/', views.DatasetReportView.as_view(), name='dataset-report'),
]
