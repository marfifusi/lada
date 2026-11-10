from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('data_contributor/', views.data_contributor, name='data_contributor'),
]