from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_page, name='signup'),
    path('verifyotp/', views.verifyotp_page, name='verify-otp'),
    path('login/', views.login_page, name='login'),
    path('', views.home_page, name='homepage'),
    path('landing_page/', views.landing_page, name='landing_page'),
    path('intern_dashboard/', views.intern_dashboard, name='intern_dashboard'),
    path('manager_dashboard/', views.mannager_dashboard, name='manager_dashboard'),
    path('profile/', views.profile_page, name='profile_page'),
    path('project/<int:pk>/', views.project_detail_page, name='project-detail-page'),
    path('tasks/<int:pk>/', views.task_detail_view, name='task-detail-page'),
    path('daily_reports/<int:pk>/', views.daily_report_detail_page, name='task-detail-page'),
]