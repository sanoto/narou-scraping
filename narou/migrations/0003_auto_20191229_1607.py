# Generated by Django 3.0.1 on 2019-12-29 16:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('narou', '0002_auto_20191227_1919'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='noveldetail',
            name='story',
        ),
        migrations.AddField(
            model_name='novel',
            name='story',
            field=models.TextField(default='', verbose_name='あらすじ'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='episode',
            name='novel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='episodes', to='narou.Novel', verbose_name='小説'),
        ),
        migrations.AlterField(
            model_name='episode',
            name='number',
            field=models.IntegerField(verbose_name='何話目か'),
        ),
        migrations.AlterField(
            model_name='noveldetail',
            name='novel',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='detail', to='narou.Novel', verbose_name='小説'),
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(verbose_name='何章目か')),
                ('name', models.CharField(max_length=500, verbose_name='名前')),
                ('novel', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='chapter', to='narou.Novel', verbose_name='小説')),
            ],
        ),
        migrations.AddField(
            model_name='episode',
            name='chapter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='episode', to='narou.Chapter', verbose_name='章'),
        ),
    ]