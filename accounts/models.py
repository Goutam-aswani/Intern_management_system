from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
from django.utils import timezone



class CustomUser(AbstractUser):
    USER_TYPE = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('intern', 'Intern'),
    )
    # GENDER = [("male", "Male"), ("Female", "Female")]
    user_type = models.CharField(default = 'intern', choices=USER_TYPE, max_length=7)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    is_manager = models.BooleanField(default=False)

class Admin(models.Model):
    user = models.OneToOneField(CustomUser,related_name ="admin_user", on_delete= models.CASCADE)
    # admin_code = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Manager(models.Model):
    user = models.OneToOneField(CustomUser,related_name ="manager", on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin,on_delete= models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # intern = models.OneToOneField(Intern,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Intern(models.Model):
    user = models.OneToOneField(CustomUser,related_name ="intern", on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager,on_delete=models.CASCADE)
    university = models.CharField(max_length=150, blank=True, null=True)
    course = models.CharField(max_length=100, blank=True, null=True)
    internship_start = models.DateField(blank=True, null=True)
    internship_end = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class Project(models.Model):
   title = models.CharField(max_length=255)
   description = models.TextField()
   start_date = models.DateField(null = True)
   end_date = models.DateField(null = True)
   manager = models.ForeignKey(CustomUser,limit_choices_to={'user_type':'manager'},on_delete=models.CASCADE,related_name='projects_managed')
   created_by = models.ForeignKey(CustomUser,limit_choices_to={'user_type__in': ['admin', 'manager']},on_delete=models.SET_NULL,null=True,related_name='projects_created')
   assigned_interns = models.ManyToManyField(CustomUser,limit_choices_to={'user_type': 'intern'},blank=True,related_name="projects")
   created_at = models.DateTimeField(auto_now_add=True)
   def __str__(self):
        return self.title

class Task(models.Model):
    TASK_STATUS = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    title = models.CharField(max_length=255,help_text="Enter a short, descriptive title for the task",unique=True)
    description = models.TextField( blank=True,help_text="Optional: add task details or steps")
    status = models.CharField(default = 'pending', choices=TASK_STATUS, max_length=15,help_text="Current status of the task")
    assigned_to = models.ForeignKey(CustomUser,limit_choices_to={'user_type': 'intern'},on_delete=models.CASCADE,related_name='assigned_intern')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_by = models.ForeignKey(CustomUser,limit_choices_to={'user_type__in': ['admin', 'manager']},on_delete=models.SET_NULL,null=True,related_name='tasks_assigned')
    due_date = models.DateField(null=True, blank=True,help_text="Optional: set a deadline for the task")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.title} → {self.assigned_to.username}"


class Daily_Report(models.Model):
    # title = models.CharField(max_length=512)
    intern = models.ForeignKey(CustomUser,limit_choices_to={'user_type': 'intern'},on_delete=models.CASCADE,related_name='daily_reports')
    task = models.ForeignKey(Task,on_delete=models.CASCADE, related_name='daily_reports')
    work_summary = models.TextField(help_text="What work did you do today?")
    time_spent = models.DurationField(help_text="Time spent on the task")
    date = models.DateField(auto_now_add=True,)
    remarks = models.TextField(blank=True, help_text="Any remarks or blockers you faced")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.date:
            self.date = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.task.pk} - {self.task.title}"