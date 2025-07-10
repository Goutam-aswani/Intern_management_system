from rest_framework import serializers
from django.utils.crypto import get_random_string
from .models import *
from django.utils import timezone
from datetime import timedelta
import re
from .tasks import *



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'phone', 'password', 'is_verified','user_type']

        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'password': {'write_only': True, 'required': True},
            'phone': {'required': True},
            'user_type' : {'required' : True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        # user_type = validated_data.get('user_type')
        user = CustomUser.objects.create_user(
        password=password,
        # user_type=user_type,
        **validated_data
            )
        user.is_verified = False
        user.is_active = False
        user.save()
        return user
    

class VerifyAccountSerializer(serializers.Serializer):
    username = serializers.CharField(required = True)
    otp = serializers.CharField(required=True, min_length=6, max_length=6)
    
class Login_Serializer(serializers.Serializer):
    username = serializers.CharField(required = True)
    password = serializers.CharField(required = True)

class ProjectSerializer(serializers.ModelSerializer):
    assigned_interns = serializers.SlugRelatedField(
        many=True,
        queryset=CustomUser.objects.filter(user_type='intern'),
        slug_field='username'
    )
    manager = serializers.SlugRelatedField(
        queryset=CustomUser.objects.filter(user_type='manager'),
        slug_field='username'
    )
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'assigned_interns', 'start_date', 'end_date','manager']
        read_only_fields = ['id']
        extra_kwargs = {
            'title': {'required': True},
            'description': {'required': False},
            # 'manager': {'required': True},
            'assigned_interns': {'required': True},
            'start_date': {'required': False},
            'end_date': {'required': False},
        }

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SlugRelatedField(
        slug_field='username',
        queryset=CustomUser.objects.filter(user_type='intern')
    )
    assigned_by = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    project = serializers.SlugRelatedField(
        slug_field='title',
        queryset=Project.objects.all()
    )
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'project', 'assigned_to', 'status', 'due_date','assigned_by']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'title': {'required': True},
            'project': {'required': True},
            # 'assigned_to': {'required': True},
            'assigned_by': {'required': False},
            'status': {'required': False},
            'due_date': {'required': False},
            'description': {'required': False},
            
        }

class Daily_Report_Serializer(serializers.ModelSerializer):
    intern = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    task = serializers.SlugRelatedField(
        slug_field='title',
        queryset=Task.objects.all()
    )
    task_title = serializers.SerializerMethodField()
    class Meta:
        model = Daily_Report
        fields = ['id', 'intern',  'task','task_title', 'date', 'work_summary', 'time_spent', 'remarks']
        read_only_fields = ['id','task_title']
        
    def get_task_title(self, obj):
        return obj.task.title
    def create(self, validated_data):
        return Daily_Report.objects.create(**validated_data)

class intern_serilizer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField()
    class Meta:
        model = Intern
        fields = ["manager"]
        
    def get_manager(self, obj):
        return obj.manager.user.username

class profile_serializer(serializers.ModelSerializer):
    intern = intern_serilizer(read_only=True)
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'phone', 'password', 'is_verified','user_type','created_at','intern']



class ProjectDetailSerializer(serializers.ModelSerializer):
    assigned_interns = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    manager = serializers.SlugRelatedField(
        queryset=CustomUser.objects.filter(user_type='manager'),
        slug_field='username'
    )
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'manager', 'assigned_interns', 
                 'start_date', 'end_date', 'created_at', 'tasks']
    
    def get_assigned_interns(self, obj):
        return [intern.username for intern in obj.assigned_interns.all()]
    
    def get_tasks(self, obj):
        from .models import Task  # Import here to avoid circular imports
        tasks = Task.objects.filter(project=obj)
        return TaskSerializer(tasks, many=True).data
    


class TaskDetailSerializer(serializers.ModelSerializer):
    project = serializers.CharField(source='project.title', read_only=True)
    assigned_to = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'project', 'assigned_to',
                  'status', 'due_date', 'created_at']
        
class DailyReportDetailSerializer(serializers.ModelSerializer):
    intern = serializers.CharField(source='intern.username', read_only=True)
    title = serializers.CharField(source='task.title', read_only=True)
    

    class Meta:
        model = Daily_Report
        fields = '__all__'



    #     intern = models.ForeignKey(CustomUser,limit_choices_to={'user_type': 'intern'},on_delete=models.CASCADE,related_name='daily_reports')
    # task = models.ForeignKey(Task,on_delete=models.CASCADE, related_name='daily_reports')
    # work_summary = models.TextField(help_text="What work did you do today?")
    # time_spent = models.DurationField(help_text="Time spent on the task")
    # date = models.DateField(auto_now_add=True,)
    # remarks = models.TextField(blank=True, help_text="Any remarks or blockers you faced")
    # created_at = models.DateTimeField(auto_now_add=True)

# class RemoveInternFromProjectSerializer(serializers.Serializer):
#     intern_id = serializers.IntegerField()
    
#     def validate_intern_id(self, value):
#         try:
#             intern = CustomUser.objects.get(id=value, user_type='intern')
#             return value
#         except CustomUser.DoesNotExist:
#             raise serializers.ValidationError("Intern not found.")


# class AssignInternSerializer(serializers.Serializer):
#     intern = serializers.PrimaryKeyRelatedField(queryset=Intern.objects.all())
#     project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())


# class InternReportViewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Daily_Report
#         fields = "__all__"


# class TaskStatusUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Task
#         fields = "__all__"


# from rest_framework import serializers
# from accounts.models import CustomUser, Admin, Manager, Intern

# class ProfileSerializer(serializers.ModelSerializer):
#     role_details = serializers.SerializerMethodField()

#     class Meta:
#         model = CustomUser
#         fields = ['id', 'username', 'email', 'phone', 'user_type', 'is_verified', 'role_details']
        
#     def get_role_details(self, obj):
#         if obj.user_type == 'admin':
#             admin = getattr(obj, 'admin_user', None)
#             return {
#                 'created_at': admin.created_at if admin else None,
#             }
#         elif obj.user_type == 'manager':
#             manager = getattr(obj, 'manager', None)
#             return {
#                 'admin': manager.admin.user.username if manager else None,
#                 'created_at': manager.created_at if manager else None,
#             }
#         elif obj.user_type == 'intern':
#             intern = getattr(obj, 'intern', None)
#             return {
#                 'admin': intern.admin.user.username if intern and intern.admin else None,
#                 'manager': intern.manager.user.username if intern and intern.manager else None,
#                 'university': intern.university,
#                 'course': intern.course,
#                 'internship_start': intern.internship_start,
#                 'internship_end': intern.internship_end,
#             }
#         return {}



# class manager_intern_list_Serializer(serializers.ModelSerializer):
#     assigned_interns = serializers.SlugRelatedField(
#     many=True,
#     slug_field='username',
#     queryset=CustomUser.objects.filter(user_type='intern')
# )

#     class Meta:
#         model = CustomUser
#         fields = ['username','assigned_interns']
#         read_only_fields = ['id']
    