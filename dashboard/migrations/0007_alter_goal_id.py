# Generated by Django 3.2.5 on 2021-08-09 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_alter_goal_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
