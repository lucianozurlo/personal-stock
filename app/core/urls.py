from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/chat/', views.chat_view, name='chat'),
    path('api/actions/', views.api_actions, name='api_actions'),
    path('api/actions/<int:action_id>/', views.api_action_detail, name='api_action_detail'),
    path('api/metrics/', views.api_metrics, name='api_metrics'),
    path('api/admin/actions/', views.api_admin_actions, name='api_admin_actions'),
    path('actions/', views.actions_page, name='actions_page'),
]
