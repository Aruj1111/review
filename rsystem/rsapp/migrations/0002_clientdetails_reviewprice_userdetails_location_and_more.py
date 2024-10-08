# Generated by Django 5.1.1 on 2024-09-28 12:24

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rsapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=255)),
                ('mobile', models.CharField(blank=True, max_length=15, null=True)),
                ('category_name', models.CharField(blank=True, max_length=100, null=True)),
                ('field_name', models.CharField(max_length=100)),
                ('stream_name', models.CharField(max_length=100)),
                ('product_name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=150)),
                ('cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('review_link', models.CharField(max_length=255)),
                ('reviewer', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ReviewPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reviewer_type', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.AddField(
            model_name='userdetails',
            name='location',
            field=models.CharField(default='jaipur', max_length=150),
        ),
        migrations.AlterField(
            model_name='userdetails',
            name='reviewer_type',
            field=models.CharField(choices=[('Admin', 'Admin'), ('Client', 'Client'), ('User', 'User')], default='User', max_length=10),
        ),
        migrations.CreateModel(
            name='UserHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_type', models.CharField(max_length=100)),
                ('review_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('location', models.CharField(max_length=150)),
                ('ip_address', models.CharField(max_length=255)),
                ('client_detail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_histories', to='rsapp.clientdetails')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_history', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
