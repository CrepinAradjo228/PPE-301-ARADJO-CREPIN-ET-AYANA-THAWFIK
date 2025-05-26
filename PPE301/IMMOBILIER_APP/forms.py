from django import forms
from .models import Proprietaire, Client, TypeBien, Utilisateur
from django.core.exceptions import ValidationError

class UtilisateurForm(forms.Form):
    nom = forms.CharField(label="Nom", max_length=255)
    prenom = forms.CharField(label="Prénom", max_length=255)
    sexe = forms.CharField(label="Sexe", max_length=255)
    age = forms.IntegerField(label="Âge", required=True)
    numero = forms.CharField(label="Numéro de téléphone", max_length=20)
    email = forms.EmailField(label="Adresse email")
    username = forms.CharField(label="Nom d'utilisateur", max_length=255)
    password = forms.CharField(label="Mot de passe" , widget=forms.PasswordInput)
    password1 = forms.CharField(label="Mot de passe" , widget=forms.PasswordInput)
    role = forms.ChoiceField(
        choices=[('client', 'Client'), ('proprietaire', 'Proprietaire')],
        label="Inscription en tant que",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    role = forms.ChoiceField(
        choices=[('client', 'Client'), ('proprietaire', 'Proprietaire')],
        label="Vous vous êtes inscrit en tant que",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class BienForm(forms.Form):
    nom = forms.CharField(label="Nom du bien",max_length=255)
    type = forms.ModelChoiceField(label="Type de bien",queryset=TypeBien.objects.all())
    localisation = forms.CharField(label="Localisation", max_length=255)
    prix = forms.FloatField(label="Prix du bien")
    etat = forms.CharField(label="Etat du bien",max_length=255)
    image = forms.ImageField(label="Inserez les images du bien")


class PublierForm(forms.Form):
    nom = forms.CharField(label="Nom du bien", max_length=255, disabled=True)
    type = forms.CharField(label="Type de bien", max_length=255, disabled=True)
    localisation = forms.CharField(label="Localisation", max_length=255, disabled=True)
    prix = forms.FloatField(label="Prix du bien", disabled=True)
    etat = forms.CharField(label="État", max_length=255, disabled=True)

    datepublication = forms.DateField(label="Entrez la date de publication")
    titrefoncier = forms.ImageField(label="Insérez une image du titre foncier")
    carterecto = forms.ImageField(label="Insérez une image de la CNI recto")
    carteverso = forms.ImageField(label="Insérez une image de la CNI verso")
    planbien = forms.ImageField(label="Insérez une image du plan du bien")
    nature_publication = forms.CharField(label="Nature de la publication", max_length=255)
    description = forms.CharField(
        label="Description", 
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}), 
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password1 = cleaned_data.get("password1")
        
        if password and password1 and password != password1:
            self.add_error("password1", "Les mots de passe ne correspondent pas.")

    def __init__(self, *args, **kwargs):
        bien = kwargs.pop('bien', None)
        super().__init__(*args, **kwargs)
        if bien:
            self.fields['nom'].initial = bien.nom
            self.fields['type'].initial = bien.type
            self.fields['localisation'].initial = bien.localisation
            self.fields['prix'].initial = bien.prix
            self.fields['etat'].initial = bien.etat

from django import forms
from .models import TypeBien, Utilisateur

class VendreForm(forms.Form):
    type_bien = forms.ModelChoiceField(
        label="Type de bien",
        queryset=TypeBien.objects.all()
    )
    prix_vente = forms.FloatField(label="Prix de vente")
    superficie = forms.FloatField(label="Superficie en m²")
    localisation = forms.CharField(label="Localisation", max_length=255)
    description = forms.CharField(label="Description", widget=forms.Textarea)
    etat_bien = forms.CharField(label="État du bien", max_length=255)
    image_principale = forms.ImageField(label="Image principale")
    titre_foncier = forms.ImageField(label="Titre foncier")
    numero_titre_foncier = forms.CharField(label="Numéro du titre foncier", max_length=255)

    proprietaire = forms.ModelChoiceField(
        label="Propriétaire",
        queryset=Utilisateur.objects.filter(role='proprietaire')
    )

from django import forms
from .models import TypeBien, Utilisateur

class LouerForm(forms.Form):
    type_bien = forms.ModelChoiceField(
        label="Type de bien",
        queryset=TypeBien.objects.all()
    )
    loyer_mensuel = forms.FloatField(label="Loyer mensuel (FCFA)")
    durée_location = forms.IntegerField(label="Durée minimale (en mois)")
    avance = forms.FloatField(label="Montant de la caution (avance)")
    localisation = forms.CharField(label="Localisation", max_length=255)
    description = forms.CharField(label="Description", widget=forms.Textarea)
    image_principale = forms.ImageField(label="Image principale")

    proprietaire = forms.ModelChoiceField(
        label="Propriétaire",
        queryset=Utilisateur.objects.filter(role='proprietaire')
    )
