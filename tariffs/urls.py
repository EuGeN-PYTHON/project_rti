from django.urls import path
from . import views
from . import views_api

urlpatterns = [
    path('', views.index, name='index'),
    path('api/lead/', views_api.create_lead, name='create_lead'),
]
