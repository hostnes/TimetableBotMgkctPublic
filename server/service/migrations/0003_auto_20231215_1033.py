# Generated by Django 3.1.2 on 2023-12-15 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0002_user_is_sender'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.TextField(blank=True, max_length=1000, verbose_name='имя')),
                ('telegram_id', models.CharField(max_length=100)),
                ('group_number', models.CharField(blank=True, max_length=5, verbose_name='номер группы')),
                ('is_sender', models.BooleanField(default=False, verbose_name='Рассылка')),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]