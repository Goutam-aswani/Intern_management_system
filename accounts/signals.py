from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.dispatch import receiver
from .models import *


# @receiver(post_save, sender=CustomUser)
# def assign_user_group(sender, instance, created, **kwargs):

#     if created:
#         instance.groups.clear()
#         group_map = {
#             'admin': 'Admin',
#             'manager': 'Manager',
#             'intern': 'Intern',
#         }
#         group_name = group_map.get(instance.user_type.lower(), 'Intern')
#         group, _ = Group.objects.get_or_create(name=group_name)
#         instance.groups.add(group)
        
#         if instance.user_type == 'admin':
#             Admin.objects.create(user=instance)
        
#         elif instance.user_type == 'manager':
#             admin = Admin.objects.first()
#             if admin:
#                 Manager.objects.create(user=instance, admin=admin)
        
#         elif instance.user_type == 'intern':
#             admin = Admin.objects.first()
#             manager = Manager.objects.first()
#             if admin and manager:
#                 Intern.objects.create(user=instance,  manager=manager)

@receiver(post_save, sender=CustomUser)
def assign_user_group(sender, instance, created, **kwargs):
    # Define group mapping
    group_map = {
        'admin': 'Admin',
        'manager': 'Manager',
        'intern': 'Intern',
    }
    
    # Get the correct group for current user_type
    target_group_name = group_map.get(instance.user_type.lower(), 'Intern')
    target_group, _ = Group.objects.get_or_create(name=target_group_name)
    
    # Remove user from all role-specific groups (Admin, Manager, Intern)
    for group_name in group_map.values():
        try:
            group = Group.objects.get(name=group_name)
            if group != target_group:
                instance.groups.remove(group)
        except Group.DoesNotExist:
            pass
    
    # Add user to the correct group
    instance.groups.add(target_group)
    
    # Handle profile creation/cleanup
    if instance.user_type == 'admin':
        # Clean up old profiles
        if hasattr(instance, 'manager'):
            instance.manager.delete()
        if hasattr(instance, 'intern'):
            instance.intern.delete()
        # Create admin profile if doesn't exist
        if not hasattr(instance, 'admin_user'):
            Admin.objects.create(user=instance)
    
    elif instance.user_type == 'manager':
        # Clean up old profiles
        if hasattr(instance, 'admin_user'):
            instance.admin_user.delete()
        if hasattr(instance, 'intern'):
            instance.intern.delete()
        # Create manager profile if doesn't exist
        if not hasattr(instance, 'manager'):
            admin = Admin.objects.first()
            if admin:
                Manager.objects.create(user=instance, admin=admin)
    
    elif instance.user_type == 'intern':
        # Clean up old profiles
        if hasattr(instance, 'admin_user'):
            instance.admin_user.delete()
        if hasattr(instance, 'manager'):
            instance.manager.delete()
        # Create intern profile if doesn't exist
        if not hasattr(instance, 'intern'):
            admin = Admin.objects.first()
            manager = Manager.objects.first()
            if admin and manager:
                Intern.objects.create(user=instance, manager=manager)