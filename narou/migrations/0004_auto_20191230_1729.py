# Generated by Django 3.0.1 on 2019-12-30 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('narou', '0003_auto_20191229_1607'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='episode',
            name='text',
        ),
        migrations.RemoveField(
            model_name='noveldetail',
            name='is_serial',
        ),
        migrations.AddField(
            model_name='episode',
            name='afterword',
            field=models.TextField(blank=True, null=True, verbose_name='あとがき'),
        ),
        migrations.AddField(
            model_name='episode',
            name='body',
            field=models.TextField(default='', verbose_name='本文'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='episode',
            name='foreword',
            field=models.TextField(blank=True, null=True, verbose_name='まえがき'),
        ),
        migrations.AddField(
            model_name='novel',
            name='is_serial',
            field=models.BooleanField(default=True, verbose_name='連載'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='episode',
            name='title',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='タイトル'),
        ),
        migrations.AlterField(
            model_name='novel',
            name='story',
            field=models.TextField(blank=True, null=True, verbose_name='あらすじ'),
        ),
    ]
