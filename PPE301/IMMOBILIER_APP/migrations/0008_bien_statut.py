# Generated by Django 5.1.6 on 2025-06-30 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IMMOBILIER_APP', '0007_vendre_statut'),
    ]

    operations = [
        migrations.AddField(
            model_name='bien',
            name='statut',
            field=models.CharField(choices=[('enregistre', 'Enregistré'), ('publie', 'Publié')], default='enregistre', max_length=10),
        ),
    ]
