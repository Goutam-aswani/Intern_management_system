from django.contrib import admin
from django.urls import path,include
from accounts.views import *
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView




urlpatterns = [
    path("admin/", admin.site.urls),
    # path("", accounts.views.homepage , name = 'homepage')
    path("api/token/",TokenObtainPairView.as_view()),
    path("api/token/refresh",TokenRefreshView.as_view()),
    path("api/register/",Register_API.as_view()),
    path("api/login/",Login_API.as_view()),
    path("api/verify-otp/",Verify_OTP_view.as_view()),
    path('api/projects/create/', Project_Create_View.as_view(), name='project_create'),
    path('api/projects/', Project_List_View.as_view(), name='project_list'),
    path('api/tasks/create/', Task_Create_APIview.as_view(), name='task_create'),
    path('api/tasks/', Task_List_APIView.as_view(), name='task_list'),
    path('api/daily_report/create/', Daily_report_create_APIview.as_view(), name='daily_report_create'),
    path('api/daily_report/', Dailt_report_list_view.as_view(), name='daily_report_list'),
    path('is-admin/', Is_admin_check_view.as_view(), name='is_admin'),
    path('users/', User_list_view.as_view(), name='user_list'),
    path('api/interns/', InternListView.as_view(), name='intern_list'),
    path('api/profile/', Profile_View.as_view(), name='profile-info'),
    path('api/manager-profile/', ManagerProfileView.as_view(), name='manager-profile'),
    path('api/projects/<int:pk>/', project_detail.as_view(), name='project-detail'),
    path('api/tasks/<int:pk>/', task_detail.as_view(), name='task-detail'),
    path('api/daily_reports/<int:pk>/', daily_report_detail.as_view(), name='daily-report-detail'),
    path('', include('accounts.urls')),
]


