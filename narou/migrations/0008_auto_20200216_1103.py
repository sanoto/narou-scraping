# Generated by Django 3.0.1 on 2020-02-16 11:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('narou', '0007_auto_20200216_0014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='writer',
            name='all_novel_length',
        ),
        migrations.RemoveField(
            model_name='writer',
            name='all_total_point',
        ),
        migrations.RemoveField(
            model_name='writer',
            name='novel_count',
        ),
    ]
