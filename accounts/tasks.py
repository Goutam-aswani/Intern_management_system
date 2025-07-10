from django.core.mail import send_mail
from django.core.mail import EmailMessage
import random
import openpyxl
from django.conf import settings
from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from io import BytesIO
from django.utils.timezone import now
# from .models import CustomUser
# from accounts.models import Manager, Intern, Daily_Report,Project


@shared_task
def send_otp_email_task(email):
    from .models import CustomUser
    subject =  "your account verification email"
    otp = random.randint(100000,999999)
    print(f"Sending email to {email} with OTP {otp}")
    message = f"your otp is {otp}"
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject,message,email_from,[email])
    print("Email should be sent now.")
    user_obj = CustomUser.objects.get(email = email)
    user_obj.otp = otp
    user_obj.save()

@shared_task
def delete_unverified_users():
    from .models import CustomUser
    time_threshold = timezone.now() - timedelta(minutes=10)
    CustomUser.objects.filter(
        is_verified=False,
        is_active=False,
        created_at__lt=time_threshold
    ).delete()

@shared_task
def manager_veification_email(username, email):
    from .models import CustomUser
    subject = "New Manager Registration - Action Required"
    admin_email = 'goutamaswani43@gmail.com'

    message = f"""
Dear Administrator,

A new manager has registered on the Intern Management System. Please review their account details below:

----------------------------------------
👤 Username : {username}
📧 Email    : {email}
----------------------------------------

This is an automated notification to help you stay updated with new registrations.

Regards,  
IMS Notification Service
"""

    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [admin_email])

        print(f"✅ Admin notified at {admin_email}")
    except Exception as e:
        print(f"❌ Failed to notify admin: {e}")



@shared_task
def send_weekly_report_email():
    from accounts.models import Manager, Intern, Daily_Report,Project
    today = now().date()
    last_week = today - timedelta(days=7)

    interns = Intern.objects.select_related('manager__user', 'user').all()

    for intern in interns:
        reports = Daily_Report.objects.filter(
            intern=intern.user,
            date__range=(last_week, today)
        ).select_related('task__project')

        if not reports.exists():
            continue
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Weekly Report"

        
        ws.append(["Task", "Project", "Date", "Time Spent", "Summary", "Remarks"])

        for report in reports:
            ws.append([
                report.task.title,
                report.task.project.title,
                str(report.date),
                str(report.time_spent),
                report.work_summary,
                report.remarks,
            ])

        # Save workbook to stream
        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)

        # Prepare email
        manager_email = intern.manager.user.email
        intern_name = intern.user.username

        subject = f"Weekly Report from Intern: {intern_name}"
        body = f"""Dear {intern.manager.user.username},

Please find attached the weekly report for your intern: {intern_name}.

This report includes daily submissions from {last_week} to {today}.

Regards,
Intern Management System"""

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.EMAIL_HOST_USER,
            to=[manager_email],
        )

        email.attach(f"{intern_name}_Weekly_Report.xlsx", stream.read(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        try:
            email.send()
            print(f"✅ Email sent to manager: {manager_email} for intern: {intern_name}")
        except Exception as e:
            print(f"❌ Failed to send email to {manager_email} for intern {intern_name}: {e}")

    return "Weekly intern reports emailed to respective managers."
