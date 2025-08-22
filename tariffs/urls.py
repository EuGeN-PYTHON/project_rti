from django.urls import path
from . import views
from . import views_api
from . import operator_views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/lead/', views_api.create_lead, name='create_lead'),

    # Операторские URLs
    path('operator/', operator_views.operator_dashboard, name='operator_dashboard'),
    path('operator/lead/<int:lead_id>/take/', operator_views.take_lead, name='take_lead'),
    path('operator/lead/<int:lead_id>/update/', operator_views.update_lead, name='update_lead'),
    path('operator/lead/<int:lead_id>/view/', operator_views.view_lead, name='view_lead'),
    path('operator/search/', operator_views.search_leads, name='search_leads'),
]