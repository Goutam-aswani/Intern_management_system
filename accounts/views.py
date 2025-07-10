from django.shortcuts import render
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from django.core.mail import send_mail
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.permissions import IsAuthenticated
from mysite.settings import EMAIL_HOST_USER
from rest_framework import status
from .tasks import send_otp_email_task
from .utils.redis_client import r
from django.shortcuts import get_object_or_404
from rest_framework import status
import random, json
from .models import *
from .serializers import *
from .permissions import *
from .tasks import *


class Register_API(APIView):
    def post(self,request):
        try:
            data = request.data
            serializer = UserSerializer(data = data)
            if serializer.is_valid():
                serializer.save()
                email = request.data.get('email')
                # send_mail('Test', 'Hello', EMAIL_HOST_USER, ['you@example.com'])
                send_otp_email_task.delay(email) 
                return Response({'status' : 200, 'data' : serializer.data , "message" : "registration successfull check email"})
            return Response({"status" : 403 ,"errors": serializer.errors, "message" : "Something went wrong"})
        except Exception as e:
            print(e)
            return Response({"status": 500, "error":serializer.errors, "message": "Internal server error"})
        
class Verify_OTP_view(APIView):
    def post(self,request):
        try:
            data = request.data
            serializer = VerifyAccountSerializer(data = data)
            if serializer.is_valid():
                username = data.get("username")
                otp = data.get("otp")
                user  = CustomUser.objects.filter(username = username)
                if not user.exists():
                    return Response({"status" : 403 ,"errors": serializer.errors, "message" : "Invalid credentials or user not active"})
                if str(user[0].otp) != str(otp):
                    print(user[0].otp)
                    return Response({"status" : 403 ,"errors": serializer.errors, "message" : "invalid otp"})
                
                user = user.first()
                user.is_verified = True
                user.is_active = True
                
                if user.user_type == 'manager':
                    manager_veification_email.delay(user.username, user.email)
                    # user.is_manager = True
                user.otp = None
                user.save()


                return Response({"status": 200,"message": "Verification successful. Please login now."})
            return Response({"status": 400, "errors": serializer.errors, "message": "Invalid input"})
        except Exception as e:
            print(e)
    

class Login_API(APIView):
    def post(self,request):
            data = request.data
            # print(request.data)
            serializer = Login_Serializer(data = data)

            if serializer.is_valid():
                username = serializer.validated_data["username"]
                password = serializer.validated_data["password"]

                user = authenticate(username = username, password = password)

                if user is None:
                     return Response({"data": {}, "message" : "invalid credentials"},status=status.HTTP_401_UNAUTHORIZED)
                if user.is_verified is False:
                     return Response({"data": {}, "message" : "your account is not verified"},status=status.HTTP_400_BAD_REQUEST)
                
                refresh = RefreshToken.for_user(user=user)

                user_type = user.user_type


                if user_type == 'manager':
                    is_manager = user.is_manager
                    return Response({
                    'refresh' : str(refresh),
                    'access': str(refresh.access_token),
                    'user_type': user_type,
                    'is_manager': is_manager,
                    'message': f"Logged in as {user_type}"
                },status=status.HTTP_200_OK)
                
                elif user_type == 'intern':    
                    return Response({
                    'refresh' : str(refresh),
                    'access': str(refresh.access_token),
                    'user_type': user_type,
                    'message': f"Logged in as {user_type}"
                },status=status.HTTP_200_OK)
            return Response({"data": {}, "message" : "Login failed"},status=status.HTTP_401_UNAUTHORIZED)

class Project_Create_View(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsAdminOrManager]

    def post(self, request):
        user = request.user
        if user.user_type == 'intern':
            return Response({'message': 'You are not allowed to create projects.'}, status=403)
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            if user.user_type == 'manager':
                serializer.save(manager=user, created_by=user)
            else:
                serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class Project_List_View(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.user_type =='admin':
            projects = Project.objects.all()
        elif user.user_type == 'manager':
            projects = Project.objects.filter(manager=user)
        elif user.user_type == 'intern':
            projects = Project.objects.filter(assigned_interns=user)
        else:
            return Response({'message': 'Invalid role'}, status=403)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

class Task_Create_APIview(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsAdminOrManager]

    def post(self, request):
        user = request.user
        
        if user.user_type not in ['admin', 'manager']:
            return Response({'message': 'Only Admins or Managers can assign tasks.'}, status=403)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(assigned_by=user)
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Task_List_APIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.user_type == 'admin':
            tasks = Task.objects.all()
        elif user.user_type == 'manager':
            tasks = Task.objects.filter(assigned_by=user)
        elif user.user_type == 'intern':
            tasks = Task.objects.filter(assigned_to=user)
        else:
            return Response({'message': 'Unauthorized user type'}, status=403)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=200)

class Daily_report_create_APIview(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsIntern]

    def post(self,request):
        user = request.user
        if user.user_type != 'intern':
            return Response({"message": "Only interns can submit daily reports."}, status=403)
        serializer = Daily_Report_Serializer(data = request.data)
        if serializer.is_valid():
            task = serializer.validated_data['task']
            if not task.project.assigned_interns.filter(id=user.id).exists():
                return Response({"message": "You are not assigned to this task's project."}, status=403)
            if task.assigned_to != user:
                return Response({"message": "This task is not assigned to you."}, status=403)


            serializer.save(intern= user)
            return Response(serializer.data,status = 201)
        return Response(serializer.errors, status= 400)

class Dailt_report_list_view(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user
        if user.user_type == 'admin':
            reports = Daily_Report.objects.all()

        elif user.user_type == 'manager':
            try:
                manager = Manager.objects.get(user=user)
                projects = Project.objects.filter(manager=manager.user)
                tasks = Task.objects.filter(project__in=projects)
                reports = Daily_Report.objects.filter(task__in=tasks)
            except Manager.DoesNotExist:
                return Response({'message': 'Manager profile not found'}, status=404)
            
        elif user.user_type == 'intern':
            if not isinstance(user, CustomUser):
                return Response({"error": "User is not valid"}, status=400)
            reports = Daily_Report.objects.filter(intern=user)
        else:
            return Response({'message': 'Invalid user role'}, status=403)
        
        serializer = Daily_Report_Serializer(reports, many=True)
        return Response(serializer.data)

class User_list_view(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsAdmin]

    def post(self,request):
        if request.user.user_type != 'admin':
            return Response({
                'error' : 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN)
        user = CustomUser.objects.all()
        serializer = UserSerializer(user,many = True)
        return Response(serializer.data)


class Profile_View(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = profile_serializer(request.user)
        return Response(serializer.data)
    

class InternListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsManager]
    
    def get(self, request):
        user = request.user
        if user.user_type == 'admin':
            interns = CustomUser.objects.filter(user_type='intern')

        elif user.user_type == 'manager':
            try:
                manager = Manager.objects.get(user=user)
                interns = CustomUser.objects.filter(user_type='intern',intern__manager = manager)
            except Manager.DoesNotExist:
                return Response({'error': 'Manager profile not found'}, status=404)
        else:
            return Response({'error': 'Permission denied'}, status=403)
        
        serializer = UserSerializer(interns, many=True)
        return Response(serializer.data)   

class Is_admin_check_view(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({"is_admin": user.is_staff or user.is_superuser})
    
def login_page(request):
    return render(request, 'login.html')

def home_page(request):
    return render(request, 'homepage.html')

def signup_page(request):
    return render(request, 'signup.html')

def verifyotp_page(request):
    return render(request, 'verifyotp.html')

def landing_page(request):
    return render(request, 'landing.html')

def intern_dashboard(request):
    return render(request, 'intern_dashboard.html')

def mannager_dashboard(request):
    return render(request, 'manager_dashboard.html')

def profile_page(request):
    return render(request, 'profile.html')

def task_detail_view(request,pk):
    return render(request,'task_detail.html')

class ManagerProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsIntern]
    
    def get(self, request):
        user = request.user
        if user.user_type != 'intern':
            return Response({'error': 'Only interns can view manager profile'}, status=403)
        
        try:
            intern = Intern.objects.get(user=user)
            if not intern.manager:
                return Response({'message': 'No manager assigned'}, status=404)
            
            manager_user = intern.manager.user
            manager_data = {
                'username': manager_user.username,
                'email': manager_user.email,
                'phone': manager_user.phone,
                'user_type': manager_user.user_type,
                'created_at': manager_user.created_at,
                'is_verified': manager_user.is_verified
            }
            
            return Response(manager_data, status=200)
            
        except Intern.DoesNotExist:
            return Response({'error': 'Intern profile not found'}, status=404)



# class ProjectDetail(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self,request,pk):
#         project = get_object_or_404(Project, id=pk)
        
#         # Check if user has permission to view this project
#         if request.user.user_type == 'manager' and project.manager != request.user:
#             return Response({'error': 'Permission denied'}, status=403)
        
#         serializer = ProjectDetailSerializer(project)
#         return Response(serializer.data)
    
class project_detail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes =[IsAuthenticated]

    def get(self,request,pk):
        user = request.user
        # project = Project.objects.filter(manager = user)
        try:
            project = Project.objects.get(pk = pk)
            # project_id = project.id
            print(Project.id)
        except Project.DoesNotExist:
            return Response({'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        # if user.user_type == 'admin':
        #     pass  # Admins can access all projects
        # elif user.user_type == 'manager' and project.manager != user:
        #     return Response({'message': 'Access denied: not your project'}, status=status.HTTP_403_FORBIDDEN)
        # elif user.user_type == 'intern' and user not in project.assigned_interns.all():
        #     return Response({'message': 'Access denied: not assigned to this project'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data)
        

class task_detail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user

        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({'message': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.user_type == 'admin':
            pass
        elif user.user_type == 'manager' and task.project.manager != user:
            return Response({'message': 'Access denied: not your task'}, status=status.HTTP_403_FORBIDDEN)
        elif user.user_type == 'intern' and task.assigned_to != user:
            return Response({'message': 'Access denied: not assigned to you'}, status=status.HTTP_403_FORBIDDEN)

        serializer = TaskDetailSerializer(task)
        return Response(serializer.data)


class daily_report_detail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        try:
            report = Daily_Report.objects.get(pk=pk)
        except Daily_Report.DoesNotExist:
            return Response({'message': 'Report not found'}, status=404)

        if user.user_type == 'admin':
            pass
        elif user.user_type == 'manager' and report.task.project.manager != user:
            return Response({'message': 'Access denied'}, status=403)
        elif user.user_type == 'intern' and report.intern != user:
            return Response({'message': 'Access denied'}, status=403)

        serializer = DailyReportDetailSerializer(report)
        return Response(serializer.data)


# class Project_List_View(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user

#         if user.user_type =='admin':
#             projects = Project.objects.all()
#         elif user.user_type == 'manager':
#             projects = Project.objects.filter(manager=user)
#         elif user.user_type == 'intern':
#             projects = Project.objects.filter(assigned_interns=user)
#         else:
#             return Response({'message': 'Invalid role'}, status=403)
#         serializer = ProjectSerializer(projects, many=True)
#         return Response(serializer.data)


def project_detail_page(request, pk):
    return render(request, 'project_detail.html')

def daily_report_detail_page(request, pk):
    return render(request, 'daily_report_detail.html')



# class AssignedInternsToManagerView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         user = request.user
#         if user.user_type == 'manager':
#             try:
#                 manager = Manager.objects.get(user=user)
#                 interns = Intern.objects.filter(manager=manager)
#                 intern_list = [intern.user.username for intern in interns]
                
#                 result = {
#                     'manager': user.username,
#                     'assigned_interns': intern_list,
#                     'intern_count': len(intern_list)
#                 }
                
#                 return Response(result, status=200)
                
#             except Manager.DoesNotExist:
#                 return Response({'error': 'Manager profile not found'}, status=404)
        
#         else:
#             return Response({'error': 'Only admins and managers can view this information'}, status=403)