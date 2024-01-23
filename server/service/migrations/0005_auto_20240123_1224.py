# Generated by Django 3.1.2 on 2024-01-23 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0004_auto_20231215_1035'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True, max_length=1000, verbose_name='имя')),
                ('telegram_id', models.CharField(max_length=20, verbose_name='телеграм айди')),
                ('group_number', models.CharField(blank=True, max_length=5, verbose_name='номер группы')),
                ('is_sender', models.BooleanField(default=False, verbose_name='Рассылка')),
            ],
        ),
        migrations.DeleteModel(
            name='Group',
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]