from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
# Create your models here.

class Utilisateur(models.Model):
    ROLES = (
        ('client', 'Client'),
        ('proprietaire', 'Proprietaire'),
    )

    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    sexe = models.CharField(max_length=255)
    age = models.IntegerField(default=18)
    numero = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    password1 = models.CharField(max_length=255 ,null=True , blank=True)
    role = models.CharField(max_length=20, choices=ROLES, default='proprietaire')
   

class Administrateur(Utilisateur):
    pass
class Proprietaire(Utilisateur):
    pass 
class Client(Utilisateur):
    pass
class TypeBien(models.Model):
    nom = models.CharField(max_length=255 , default= "")
    def __str__(self):
        return self.nom

class Bien(models.Model):
    nom = models.CharField(max_length=255)
    type = models.ForeignKey(TypeBien, on_delete=models.CASCADE)
    localisation = models.CharField(max_length=255)
    prix = models.FloatField()
    etat = models.CharField(max_length=255)
    image = models.ImageField(upload_to='biens/')

class Publication(models.Model):
    titrefoncier = models.ImageField(upload_to='Piècesbiens/',null=False , blank = False)
    carterecto = models.ImageField(upload_to='Piècesbiens/', null=True, blank=False)
    carteverso = models.ImageField(upload_to='Piècesbiens/', null = True , blank= False)
    planbien = models.ImageField(upload_to='Piècesbiens/', null= True , blank= False)
    nature_publication = models.CharField(max_length=255)
    description = models.TextField() 
    datepublication = models.DateField(default=datetime.date.today)
    bien = models.ForeignKey('Bien', on_delete=models.CASCADE, related_name='publications')
    
    

    def __str__(self):
        return f"Publication pour {self.bien.nom}"

class Acheter(models.Model):
    date_achat = models.DateField()
    Bien = models.ForeignKey(Bien , on_delete=models.CASCADE)
    Client = models.ForeignKey(Client , on_delete=models.CASCADE)

class Louer(models.Model):
    date_location = models.DateField()
    duree_location = models.IntegerField(default=0)
    Bien = models.ForeignKey(Bien , on_delete=models.CASCADE)
    Client = models.ForeignKey(Client , on_delete=models.CASCADE)



