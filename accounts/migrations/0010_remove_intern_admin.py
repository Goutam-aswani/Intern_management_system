# Generated by Django 5.2.3 on 2025-07-07 01:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0009_daily_report_created_at_project_created_at_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="intern",
            name="admin",
        ),
    ]
