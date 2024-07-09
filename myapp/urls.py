# myapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('generate-image/', views.generate_image, name='generate_image'), 
    path('upload/', views.upload_note_view, name='upload_note'),
    path('questions/<int:note_id>/', views.generate_questions_view, name='generate_questions'),

]