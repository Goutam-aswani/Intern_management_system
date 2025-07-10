from django.contrib import admin
from .models import *


class user_display(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
        "created_at",
        "is_staff",
        "is_verified",
        "user_type"]
    list_filter = ['user_type',]
    filter_horizontal = ("groups",)
    search_fields = ['email','username']
    ordering = ('created_at',)

    fieldsets =[ ("Basic info", {"fields" : ["username","email"]}),
                ("additional info", {"fields":["is_superuser","is_active","phone","user_type","is_verified","user_permissions","groups"]}),
                ("Authentication Information",{"fields":['password','is_manager']})]

class Admin_display(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)

class Manager_display(admin.ModelAdmin):
    list_display = ('user', 'admin', 'created_at')
    search_fields = ('user__username', 'admin__user__username')
    list_filter = ('admin', 'created_at')

class Intern_display(admin.ModelAdmin):
    list_display = ('user', 'manager', 'university', 'course', 'internship_start', 'internship_end')
    search_fields = ('user__username', 'university', 'course')
    list_filter = ( 'manager', 'internship_start', 'internship_end')

class Project_display(admin.ModelAdmin):
    list_display = ('title', 'manager', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    list_filter = ('manager', 'start_date', 'end_date')
    filter_horizontal = ('assigned_interns',)

class Task_display(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'due_date')
    list_filter = ('status', 'due_date', 'project')
    search_fields = ('title', 'description')

class DailyReport_display(admin.ModelAdmin):
    list_display = ('intern', 'task', 'date', 'time_spent')
    list_filter = ('date', 'intern')
    search_fields = ('work_summary', 'remarks')

admin.site.register(CustomUser,user_display)
admin.site.register(Admin,Admin_display)
admin.site.register(Manager,Manager_display)
admin.site.register(Intern,Intern_display)
admin.site.register(Project,Project_display)
admin.site.register(Task,Task_display)
admin.site.register(Daily_Report, DailyReport_display)
