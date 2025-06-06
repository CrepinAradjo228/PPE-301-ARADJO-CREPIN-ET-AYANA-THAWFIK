# Generated by Django 5.1.6 on 2025-05-25 20:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IMMOBILIER_APP', '0003_alter_utilisateur_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='louer',
            name='Bien',
        ),
        migrations.RemoveField(
            model_name='louer',
            name='Client',
        ),
        migrations.RemoveField(
            model_name='louer',
            name='date_location',
        ),
        migrations.RemoveField(
            model_name='louer',
            name='duree_location',
        ),
        migrations.AddField(
            model_name='louer',
            name='avance',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='louer',
            name='description',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='louer',
            name='durée_location',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='louer',
            name='image_principale',
            field=models.ImageField(default='', upload_to='biens_loues/'),
        ),
        migrations.AddField(
            model_name='louer',
            name='localisation',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='louer',
            name='loyer_mensuel',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='louer',
            name='proprietaire',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='IMMOBILIER_APP.proprietaire'),
        ),
        migrations.AddField(
            model_name='louer',
            name='type_bien',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='IMMOBILIER_APP.typebien'),
        ),
        migrations.AlterField(
            model_name='bien',
            name='etat',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='bien',
            name='prix',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Vendre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prix_vente', models.FloatField()),
                ('superficie', models.FloatField()),
                ('localisation', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('etat_bien', models.CharField(max_length=255)),
                ('image_principale', models.ImageField(upload_to='biens_vendus/')),
                ('proprietaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='IMMOBILIER_APP.proprietaire')),
                ('type_bien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='IMMOBILIER_APP.typebien')),
            ],
        ),
        migrations.DeleteModel(
            name='Acheter',
        ),
    ]
