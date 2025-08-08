from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from django.utils import timezone
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
    type = models.CharField(max_length=255)
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
    ('enregistre', 'Enregistré (En attente de publication)'), 
    ('en_attente', 'En attente de validation (pour l\'administrateur)'), 
    ('publie', 'Publié'), 
    ('refuse', 'Refusé'), 
    ]
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    type_bien = models.CharField(max_length=255)
    prix_vente = models.FloatField()
    superficie = models.FloatField()  # en m²
    localisation = models.CharField(max_length=255)
    description = models.TextField()
    etat_bien = models.CharField(max_length=255)
    image_principale = models.ImageField(upload_to='biens_vendus/')
    titre_foncier = models.ImageField(upload_to='titres_fonciers/', default="")
    numero_titre_foncier = models.CharField(max_length=255, unique=True, default="")
    cloturer = models.BooleanField(default=False, help_text="Indique si la vente est clôturée ou non")
    
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
    type_bien = models.CharField(max_length=255, default="")
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
    date_demande = models.DateTimeField(default=timezone.now) 
    date_traitement = models.DateTimeField(null=True, blank=True)
    duree_location_mois = models.PositiveIntegerField(null=True, blank=True, help_text="Durée minimale souhaitée par le client (en mois)")
    est_traitee = models.BooleanField(default=False) 
    

    def __str__(self):
        if self.bien_vente:
            return f"Demande de {self.demandeur.username} pour vente ID {self.bien_vente.pk}"
        elif self.bien_location:
            return f"Demande de {self.demandeur.username} pour location ID {self.bien_location.pk}"
        return f"Demande de {self.demandeur.username} (bien non spécifié)"

    def _traiter_vente(self):
        """
        Clôture le bien mis en vente si une transaction 'vendu' est associée à cette demande.
        """
        if self.bien_vente:
            transaction = Transaction.objects.filter(
                demande=self,
                statut_bien_apres_transaction='vendu'
            ).first()
            if transaction:
                bien = self.bien_vente
                bien.statut = 'vendu'
                bien.cloturer = True
                bien.save()

               
            
           


# Nouvelle définition des STATUT_BIEN pour clarifier
STATUT_BIEN_TRANSACTION_CHOICES = [
    ('vendu', 'Vendu'),
    ('loue', 'Loué'),
    ('annule', 'Annulé'), # Optionnel si vous voulez suivre les transactions annulées aussi
]

class Transaction(models.Model):  
    # Clé étrangère vers le bien vendu ou loué (peut être NULL si un bien est supprimé, mais mieux de le garder)
    bien_vente = models.ForeignKey(
        Vendre,
        on_delete=models.SET_NULL, # Le bien n'est pas supprimé si la transaction l'est
        null=True, blank=True,
        related_name='transactions_vente',
        verbose_name="Bien Vendu"
    )
    bien_location = models.ForeignKey(
        Louer,
        on_delete=models.SET_NULL, # Le bien n'est pas supprimé si la transaction l'est
        null=True, blank=True,
        related_name='transactions_location',
        verbose_name="Bien Loué"
    )

    # Clé étrangère vers la demande qui a mené à cette transaction
    demande = models.OneToOneField(
        DemandeBien,
        on_delete=models.SET_NULL, # La demande n'est pas supprimée si la transaction l'est
        null=True, blank=True,
        related_name='transaction_liee',
        verbose_name="Demande Associée"
    )

    # Détails du propriétaire (pour un historique même si le propriétaire est supprimé)
    proprietaire = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='transactions_proprietaire',
        verbose_name="Propriétaire du Bien"
    )

    # Détails du client (celui qui a fait la demande)
    client_nom = models.CharField(max_length=100, verbose_name="Nom du Client")
    client_email = models.EmailField(verbose_name="Email du Client")
    client_telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone du Client")

    # Type de transaction (Vendu ou Loué)
    type_transaction = models.CharField(max_length=10,choices=STATUT_BIEN_TRANSACTION_CHOICES,verbose_name="Type de Transaction")

    # Date de la transaction
    date_transaction = models.DateTimeField(default=timezone.now, verbose_name="Date de la Transaction")

    # Montant de la transaction (prix de vente ou loyer mensuel initial/avance)
    montant_transaction = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Montant de la Transaction")

    # Champ pour le statut final du bien après transaction (ex: 'vendu', 'loue')
    statut_bien_apres_transaction = models.CharField(max_length=10,choices=STATUT_BIEN_TRANSACTION_CHOICES,verbose_name="Statut du Bien Après Transaction")

    date_fin_location = models.DateField(null=True, blank=True)
    date_debut_location = models.DateField(null=True, blank=True, verbose_name="Date de Début de Location")


    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-date_transaction'] # Ordonner par la date la plus récente

    def __str__(self):
        bien_info = ""
        if self.bien_vente:
            bien_info = f"Bien Vente ID: {self.bien_vente.id}"
        elif self.bien_location:
            bien_info = f"Bien Location ID: {self.bien_location.id}"
        return f"Transaction {self.type_transaction} - {bien_info} avec {self.client_nom} le {self.date_transaction.strftime('%Y-%m-%d')}"

class RenouvelerLocation(models.Model):
    nom_complet = models.CharField(max_length=255)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    duree_nouvelle_location = models.PositiveIntegerField(help_text="Durée en mois")
    bien = models.ForeignKey(Louer, on_delete=models.CASCADE)
    date_renouvellement_demande = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nom_complet} - {self.bien.titre}"

