# Generated by Django 5.1.5 on 2025-02-04 22:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('glocal', '0003_alter_seguroaccidentepersonal_cobertura'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='archivo',
            name='matriz',
        ),
        migrations.AddField(
            model_name='archivo',
            name='aseguradora',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='glocal.aseguradora'),
            preserve_default=False,
        ),
    ]
