# Generated by Django 5.1.6 on 2025-02-07 09:41

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legal_assistant', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueryJob',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('query', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('result', models.JSONField(blank=True, null=True)),
            ],
        ),
    ]
