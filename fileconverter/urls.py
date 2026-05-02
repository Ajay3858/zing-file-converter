from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('jpg-to-pdf/', views.jpg_to_pdf, name='jpg_to_pdf'),
    path('pdf-to-jpg/', views.pdf_to_jpg, name='pdf_to_jpg'),

    path('pdf-to-word/', views.pdf_to_word, name='pdf_to_word'),
    path('word-to-pdf/', views.word_to_pdf, name='word_to_pdf'),

    path('download/', views.download, name='download'),
]