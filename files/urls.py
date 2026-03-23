from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload'),
    path('download/', views.download_file, name='download'),
    path('delete/', views.delete_file, name='delete'),
    path('create-folder/', views.create_folder, name='create_folder'),
]
