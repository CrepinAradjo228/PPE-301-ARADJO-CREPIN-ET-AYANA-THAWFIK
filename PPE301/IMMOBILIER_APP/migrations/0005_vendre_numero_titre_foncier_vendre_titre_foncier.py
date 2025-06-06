# Generated by Django 5.1.6 on 2025-05-25 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IMMOBILIER_APP', '0004_remove_louer_bien_remove_louer_client_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendre',
            name='numero_titre_foncier',
            field=models.CharField(default='', max_length=255, unique=True),
        ),
        migrations.AddField(
            model_name='vendre',
            name='titre_foncier',
            field=models.ImageField(default='', upload_to='titres_fonciers/'),
        ),
    ]
