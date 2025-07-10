# from django.core.management.base import BaseCommand
# from accounts.models import CustomUser, Admin, Manager, Intern


# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         for user in CustomUser.objects.all():
#             if user.user_type == 'admin' and not hasattr(user, 'admin_user'):
#                 Admin.objects.create(user=user)
#                 print(f"Created Admin profile for {user.username}")
            
#             elif user.user_type == 'manager' and not hasattr(user, 'manager'):
#                 admin = Admin.objects.first()
#                 if admin:
#                     Manager.objects.create(user=user, admin=admin)
#                     print(f"Created Manager profile for {user.username}")
            
#             elif user.user_type == 'intern' and not hasattr(user, 'intern'):
#                 admin = Admin.objects.first()
#                 manager = Manager.objects.first()
#                 if admin and manager:
#                     Intern.objects.create(user=user, manager=manager)
#                     print(f"Created Intern profile for {user.username}")
        
#         print("Done!")

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from accounts.models import CustomUser, Admin, Manager, Intern

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Define group mapping
        group_map = {
            'admin': 'Admin',
            'manager': 'Manager',
            'intern': 'Intern',
        }
        
        for user in CustomUser.objects.all():
            # Get the correct group for current user_type
            target_group_name = group_map.get(user.user_type.lower(), 'Intern')
            target_group, _ = Group.objects.get_or_create(name=target_group_name)
            
            # Remove user from incorrect role groups
            for group_name in group_map.values():
                try:
                    group = Group.objects.get(name=group_name)
                    if group != target_group and user.groups.filter(name=group_name).exists():
                        user.groups.remove(group)
                        print(f"Removed {user.username} from {group_name} group")
                except Group.DoesNotExist:
                    pass
            
            # Add user to correct group if not already there
            if not user.groups.filter(name=target_group_name).exists():
                user.groups.add(target_group)
                print(f"Added {user.username} to {target_group_name} group")
            
            # Handle profile cleanup and creation
            if user.user_type == 'admin':
                # Clean up old profiles
                if hasattr(user, 'manager'):
                    user.manager.delete()
                    print(f"Deleted Manager profile for {user.username}")
                if hasattr(user, 'intern'):
                    user.intern.delete()
                    print(f"Deleted Intern profile for {user.username}")
                # Create admin profile if doesn't exist
                if not hasattr(user, 'admin_user'):
                    Admin.objects.create(user=user)
                    print(f"Created Admin profile for {user.username}")
            
            elif user.user_type == 'manager':
                # Clean up old profiles
                if hasattr(user, 'admin_user'):
                    user.admin_user.delete()
                    print(f"Deleted Admin profile for {user.username}")
                if hasattr(user, 'intern'):
                    user.intern.delete()
                    print(f"Deleted Intern profile for {user.username}")
                # Create manager profile if doesn't exist
                if not hasattr(user, 'manager'):
                    admin = Admin.objects.first()
                    if admin:
                        Manager.objects.create(user=user, admin=admin)
                        print(f"Created Manager profile for {user.username}")
            
            elif user.user_type == 'intern':
                # Clean up old profiles
                if hasattr(user, 'admin_user'):
                    user.admin_user.delete()
                    print(f"Deleted Admin profile for {user.username}")
                if hasattr(user, 'manager'):
                    user.manager.delete()
                    print(f"Deleted Manager profile for {user.username}")
                # Create intern profile if doesn't exist
                if not hasattr(user, 'intern'):
                    admin = Admin.objects.first()
                    manager = Manager.objects.first()
                    if admin and manager:
                        Intern.objects.create(user=user, manager=manager)
                        print(f"Created Intern profile for {user.username}")
        
        print("Done!")
        