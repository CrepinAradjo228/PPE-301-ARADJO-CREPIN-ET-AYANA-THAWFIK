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
    def __str__(self):
        return f"{self.nom} {self.prenom}"

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
    STATUT_CHOICES = [
        ('enregistre', 'Enregistré'),
        ('publie', 'Publié'),
        ('disponible', 'Disponible'),
    ]
    nom = models.CharField(max_length=255)
    type = models.ForeignKey(TypeBien, on_delete=models.CASCADE)
    localisation = models.CharField(max_length=255)
    prix = models.FloatField(null=True, blank=True)
    etat = models.CharField(max_length=255 ,null=True, blank=True)
    image = models.ImageField(upload_to='biens/')
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='enregistre', # Par défaut, un bien est "enregistré" lors de sa création
    )
    proprietaire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)



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

class Vendre(models.Model):
    STATUTS = [
    ('enregistre', 'Enregistré (En attente de publication)'), # Le statut initial après création par le propriétaire
    ('en_attente', 'En attente de validation (pour l\'administrateur)'), # Statut quand il est en revue par l'admin
    ('publie', 'Publié'), # Statut quand il est validé et visible
    ('refuse', 'Refusé'), # Si l'admin refuse
    ]
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    type_bien = models.ForeignKey(TypeBien, on_delete=models.CASCADE)
    prix_vente = models.FloatField()
    superficie = models.FloatField()  # en m²
    localisation = models.CharField(max_length=255)
    description = models.TextField()
    etat_bien = models.CharField(max_length=255)
    image_principale = models.ImageField(upload_to='biens_vendus/')
    titre_foncier = models.ImageField(upload_to='titres_fonciers/', default="")
    numero_titre_foncier = models.CharField(max_length=255, unique=True, default="")
    
    proprietaire = models.ForeignKey(Utilisateur,  on_delete=models.CASCADE,limit_choices_to={'role': 'proprietaire'}  )
    def __str__(self):
        return f"{self.type_bien} - {self.localisation}"
    
    @property
    def type_bien_str(self):
        return 'vendre'


class Louer(models.Model):
    STATUTS = [
        ('enregistre', 'Enregistré (En attente de publication)'),
        ('en_attente', 'En attente de validation (pour l\'administrateur)'),
        ('publie', 'Publié'),
        ('refuse', 'Refusé'),
    ]
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    type_bien = models.ForeignKey(TypeBien, on_delete=models.CASCADE, default=None)
    loyer_mensuel = models.FloatField(default=0)
    durée_location = models.IntegerField(default=1) 
    avance = models.FloatField(default=0)
    localisation = models.CharField(max_length=255, default="")
    description = models.TextField(default="")
    image_principale = models.ImageField(upload_to='biens_loues/', default="")

    proprietaire = models.ForeignKey(
        Utilisateur,  
        on_delete=models.CASCADE,
        default=None,
        limit_choices_to={'role': 'proprietaire'}  
    )
    def __str__(self):
        return f"{self.type_bien} - {self.localisation} ({self.statut})"
    
    @property
    def type_bien_str(self):
        return 'louer'

class DemandeBien(models.Model):
    TYPES_DEMANDE_CHOICES = (
        ('vente', 'Demande pour une vente'),
        ('location', 'Demande pour une location'),
    )
    bien_vente = models.ForeignKey(Vendre, on_delete=models.CASCADE,null=True,  blank=True, related_name='demandes_vente')
    bien_location = models.ForeignKey(Louer, on_delete=models.CASCADE,null=True, blank=True, related_name='demandes_location')
    nom_complet = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    type_demande = models.CharField(max_length=10, choices=TYPES_DEMANDE_CHOICES) 
    message = models.TextField(blank=True, null=True) 
    date_demande = models.DateTimeField(auto_now_add=True) 
    est_traitee = models.BooleanField(default=False) 

    def __str__(self):
        if self.bien_vente:
            return f"Demande de {self.demandeur.username} pour vente ID {self.bien_vente.pk}"
        elif self.bien_location:
            return f"Demande de {self.demandeur.username} pour location ID {self.bien_location.pk}"
        return f"Demande de {self.demandeur.username} (bien non spécifié)"