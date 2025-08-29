from urllib import request
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render , redirect,get_object_or_404
from .models import Proprietaire,Client,Utilisateur,Bien,Publication,Vendre,Louer,DemandeBien,Transaction,RenouvelerLocation,DocumentsTransactionVente,AdminLogin,ImageBien  
from .forms import UtilisateurForm,ConnexionForm,BienForm,PublierForm,VendreForm,LouerForm,DemandeBienForm,RenouvelerLocationForm,DocumentsTransactionVenteForm,AdminLoginForm  
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import make_password , check_password
from django.contrib import messages
from django.urls import reverse
from django.db import transaction as db_transaction
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import date
from .utils import admin_required
from django.http import Http404

def home(request):
    return render(request, 'index.html')
def property(request):
    return render(request , 'properties.html')
def contact(request):
    return render(request , 'contact.html')
def landpage(request):
    return render(request , 'homepage.html')
def homepage(request):
    return render(request , 'landpage.html')

def dashboard(request):
    utilisateur_id = request.session.get('utilisateur_id', None)

    if utilisateur_id is None:
        messages.error(request, "Vous devez être connecté pour voir cette page.")
        return redirect('connexion')

    proprietaire_obj = get_object_or_404(Utilisateur, pk=utilisateur_id)

    # Compter les biens enregistrés
    nombre_biens_enregistres = Bien.objects.filter(proprietaire=proprietaire_obj, statut='enregistre').count()

    # Compter les biens publiés
    nombre_biens_publies_vente = Vendre.objects.filter(proprietaire=proprietaire_obj, statut='valide').count()
    nombre_biens_publies_location = Louer.objects.filter(proprietaire=proprietaire_obj, statut='disponible').count()
    nombre_biens_refuses_vente = Vendre.objects.filter(proprietaire=proprietaire_obj, statut='refuse').count()
    nombre_biens_refuses_location = Louer.objects.filter(proprietaire=proprietaire_obj, statut='refuse').count()
    nombre_biens_refuses = nombre_biens_refuses_vente + nombre_biens_refuses_location
    nombre_biens_publies = nombre_biens_publies_vente + nombre_biens_publies_location

    # Compter les demandes en attente
    nombre_demandes_en_attente = DemandeBien.objects.filter(
        bien_vente__proprietaire=proprietaire_obj,
        est_traitee=False
    ).count() + DemandeBien.objects.filter(
        bien_location__proprietaire=proprietaire_obj,
        est_traitee=False
    ).count()

    context = {
        'nombre_biens_refuses': nombre_biens_refuses,
        'proprietaire': proprietaire_obj,
        'proprietaire_id': proprietaire_obj.id,
        'nombre_biens_publies': nombre_biens_publies,
        'nombre_biens_enregistres': nombre_biens_enregistres,
        'nombre_demandes_en_attente': nombre_demandes_en_attente,
    }
    return render(request, 'Dashboard.html', context)


def inscription(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            password1 = form.cleaned_data['password1']
            if password != password1:
                form.add_error('password1', "Les mots de passe ne correspondent pas.")
            else:
                utilisateur = Utilisateur(
                    username=form.cleaned_data['username'],
                    password=make_password(password),
                    password1=password1,  # Stocker le mot de passe non haché
                    nom=form.cleaned_data['nom'],
                    prenom=form.cleaned_data['prenom'],
                    sexe=form.cleaned_data['sexe'],
                    age=form.cleaned_data['age'],
                    numero=form.cleaned_data['numero'],
                    email=form.cleaned_data['email'],
                    role=form.cleaned_data['role'],
                )
                utilisateur.save()
                # NE PAS connecter l'utilisateur ici
                return redirect('connexion')
    else:
        form = UtilisateurForm()
    return render(request, 'inscription.html', {'form': form})


def connexion_view(request):
    erreur = None

    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username_saisi = form.cleaned_data['username']
            password_saisi = form.cleaned_data['password']
            role_saisi = form.cleaned_data['role']

            try:
                utilisateur = Utilisateur.objects.get(username=username_saisi)
            except Utilisateur.DoesNotExist:
                utilisateur = None

            if utilisateur is None:
                erreur = "Nom d'utilisateur incorrect."
            elif not check_password(password_saisi, utilisateur.password):
                erreur = "Mot de passe incorrect."
            elif utilisateur.role != role_saisi:
                erreur = "Rôle incorrect pour cet utilisateur."
            else:
                request.session['utilisateur_id'] = utilisateur.id
                request.session['utilisateur_role'] = utilisateur.role
                # Redirection selon le rôle uniquement
                if utilisateur.role == 'client':
                    return redirect('property')
                else:
                    return redirect('dashboard')  # Redirection pour les propriétaires
    else:
        form = ConnexionForm()

    return render(request, 'connexion.html', {'form': form, 'erreur': erreur})

def deconnexion_view(request):
    # Supprime les informations de session
    if 'utilisateur_id' in request.session:
        del request.session['utilisateur_id']
    if 'utilisateur_role' in request.session:
        del request.session['utilisateur_role']

    # Redirige vers la page d'accueil ou de connexion
    return redirect('home')

@login_required
def tableau_de_bord(request):
    return render(request, 'index.html')


def EnregistrerBien(request):
    utilisateur_id = request.session.get('utilisateur_id', None)
    if utilisateur_id is None:
        return redirect('connexion')

    proprietaire_obj = get_object_or_404(Utilisateur, pk=utilisateur_id)

    if request.method == "POST":
        form = BienForm(request.POST)
        images = request.FILES.getlist('images') # Récupère la liste des images

        # Vérifier le nombre d'images
        if not (3 <= len(images) <= 4):
            messages.error(request, 'Veuillez télécharger entre 3 et 4 images.')
            return redirect('enregistrer')

        if form.is_valid():
            # Créer le bien manuellement avec les données du formulaire
            nouv_bien = Bien.objects.create(
                nom=form.cleaned_data['nom'],
                type=form.cleaned_data['type'],
                localisation=form.cleaned_data['localisation'],
                prix=form.cleaned_data['prix'],
                etat=form.cleaned_data['etat'],
                proprietaire=proprietaire_obj,
                statut='enregistre'
            )

            # Enregistrer les images liées au bien
            for image in images:
                ImageBien.objects.create(bien=nouv_bien, image=image)

            messages.success(request, 'Votre bien a été enregistré avec succès!')
            return redirect('listebien', proprietaire_id=utilisateur_id)
        else:
            print("Formulaire invalide :", form.errors)
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        form = BienForm()
        
    return render(request, 'register.html', {'form': form})

def modifier_bien(request, bien_id):
    # Récupérer l'objet Bien à modifier
    bien = get_object_or_404(Bien, id=bien_id)
    
    # Assurez-vous que seul le propriétaire peut modifier son bien
    utilisateur_id = request.session.get('utilisateur_id')
    if not utilisateur_id or bien.proprietaire.id != utilisateur_id:
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce bien.")
        return redirect('listebien', proprietaire_id=utilisateur_id)

    if request.method == "POST":
        form = BienForm(request.POST)
        
        if form.is_valid():
            # Mettre à jour manuellement les champs de l'objet Bien
            bien.nom = form.cleaned_data['nom']
            bien.type = form.cleaned_data['type']
            bien.localisation = form.cleaned_data['localisation']
            bien.prix = form.cleaned_data['prix']
            bien.etat = form.cleaned_data['etat']
            
            # Gérer les images
            images_a_supprimer_ids = request.POST.getlist('images_a_supprimer')
            for image_id in images_a_supprimer_ids:
                try:
                    ImageBien.objects.get(pk=image_id, bien=bien).delete()
                except ImageBien.DoesNotExist:
                    pass # Ignorer si l'image n'existe pas

            images_a_ajouter = request.FILES.getlist('images_a_ajouter')
            
            # Vérifier si l'utilisateur essaie de télécharger trop d'images
            # On ajoute le nombre d'images à ajouter au nombre d'images existantes après suppression
            nombre_images_restantes = bien.images.count()
            if (nombre_images_restantes + len(images_a_ajouter)) > 4:
                messages.error(request, 'Le nombre total d\'images ne peut pas dépasser 4.')
                return render(request, "modifier_bien.html", {"form": form, "bien": bien})
            
            # Enregistrer les nouvelles images
            for image_file in images_a_ajouter:
                ImageBien.objects.create(bien=bien, image=image_file)

            bien.save()
            
            messages.success(request, 'Le bien a été modifié avec succès!')
            return redirect('listebien', proprietaire_id=utilisateur_id)
        else:
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
            # Pour le GET, initialiser le formulaire avec les données du bien
    else:
        # Pré-remplissage du formulaire pour le GET
        form = BienForm(initial={
            'nom': bien.nom,
            'type': bien.type,
            'localisation': bien.localisation,
            'prix': bien.prix,
            'etat': bien.etat,
        })
        
    return render(request, "modifier_bien.html", {"form": form, "bien": bien})

def supprimer_bien(request, bien_id):
    # Récupérer l'objet Bien à supprimer
    bien = get_object_or_404(Bien, id=bien_id)
    
    # Assurez-vous que seul le propriétaire peut supprimer son bien
    utilisateur_id = request.session.get('utilisateur_id')
    if not utilisateur_id or bien.proprietaire.id != utilisateur_id:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer ce bien.")
        return redirect('listebien', proprietaire_id=utilisateur_id)

    if request.method == 'POST':
        bien.delete()
        messages.success(request, "Le bien a été supprimé avec succès.")
        return redirect('listebien', proprietaire_id=utilisateur_id)
    
    # Pour la confirmation (requête GET), vous pouvez rendre une page de confirmation
    return render(request, "confirmer_suppression.html", {"bien": bien})

def listeBien(request, proprietaire_id):
    proprietaire_obj = get_object_or_404(Utilisateur, pk=proprietaire_id)
    
    biens = Bien.objects.filter(proprietaire=proprietaire_obj, statut='enregistre')
    context = {
       "listebiens": biens,
        "proprietaire_concerne": proprietaire_obj, # Utile pour afficher le nom du propriétaire sur la page
    }
    return render(request, "listebien.html", context)

def PublierBien(request, id):
    bien = get_object_or_404(Bien, id=id)
    request.session['bien_en_publication_id'] = bien.id
    return redirect('choixpublication' ,id=bien.id) 

def biens_refuses(request):
    # Récupérer l'ID de l'utilisateur depuis la session
    utilisateur_id = request.session.get('utilisateur_id', None)
    
    # Si l'ID de l'utilisateur n'est pas dans la session, le rediriger vers la page de connexion
    if utilisateur_id is None:
        return redirect('connexion')
        
    # Récupérer l'objet Utilisateur ou renvoyer une erreur 404 si non trouvé
    proprietaire_obj = get_object_or_404(Utilisateur, pk=utilisateur_id)
    
    # Récupérer tous les biens refusés appartenant à cet utilisateur
    biens_vente_refuses = Vendre.objects.filter(proprietaire=proprietaire_obj, statut='refuse')
    biens_location_refuses = Louer.objects.filter(proprietaire=proprietaire_obj, statut='refuse')

    context = {
        'proprietaire': proprietaire_obj,  # Assurez-vous d'avoir l'objet Proprietaire
        'biens_vente_refuses': biens_vente_refuses,
        'biens_location_refuses': biens_location_refuses,
    }
    
    return render(request, 'biens_refuses.html', context)

def listePublication(request):
    # Récupère tous les biens en vente publiés et non clôturés
    ventes = Vendre.objects.filter(statut='valide', cloturer=False)
    
    # Récupère les locations disponibles ou louées
    locations = Louer.objects.filter(statut__in=['disponible', 'loue'])

    # Logique de mise à jour du statut dans la boucle
    for location in locations:
        if location.statut == 'loue':
            last_transaction = location.transactions_location.order_by('-date_fin_location').first()
            
            if last_transaction and last_transaction.date_fin_location and last_transaction.date_fin_location < date.today():
                location.statut = 'disponible'
                location.save()

    # Le code a été réécrit pour supprimer la deuxième requête redondante.
    # On n'a pas besoin de rafraîchir la liste "locations" car on a déjà les objets mis à jour en mémoire.
    
    # Envoi des listes distinctes au template
    return render(request, "properties.html", {
        'biens_en_vente': ventes,
        'biens_en_location': locations,
    })


def choix_publication(request, id): # La signature de la fonction doit accepter l'ID
    bien = get_object_or_404(Bien, id=id) 
    return render(request, 'choix_publication.html', {'bien': bien})

def bienpublies(request):
    # Récupérer l'id du propriétaire depuis la session
    utilisateur_id = request.session.get('utilisateur_id', None)

    if utilisateur_id is None:
        return redirect('connexion')

    # Récupérer l'objet Utilisateur correspondant
    proprietaire_obj = get_object_or_404(Utilisateur, pk=utilisateur_id)

    # Filtrer uniquement les biens de ce propriétaire ayant le statut 'publie'
    listebiens_vente_publies = Vendre.objects.filter(proprietaire=proprietaire_obj, statut='valide')
    listebiens_location_publies = Louer.objects.filter(proprietaire=proprietaire_obj, statut='disponible')

    context = {
        "listebiens_vente_publies": listebiens_vente_publies,
        "listebiens_location_publies": listebiens_location_publies,
        "proprietaire_concerne": proprietaire_obj,
    }

    return render(request, "bienpublies.html", context)

# votre_app/views.py

def ajouter_vente(request, publication_id=None):
    images_existantes = None
    titre_foncier_existant = None
    # Mode Modification
    if publication_id:
        instance_vente = get_object_or_404(Vendre, id=publication_id)
        # On n'a plus besoin du modèle 'Bien' pour la republication
        bien = None 
        images_existantes = ImageBien.objects.filter(bien_vente=instance_vente)
        titre_foncier_existant = instance_vente.titre_foncier
    # Mode Création
    else:
        bien_id = request.GET.get('bien_id') 
        if not bien_id:
            messages.error(request, "ID de bien initial manquant.")
            return redirect('listebien')
        # On a besoin du modèle 'Bien' uniquement pour la création initiale
        bien = get_object_or_404(Bien, id=bien_id)
        instance_vente = None

    utilisateur_connecte = None
    if request.session.get('utilisateur_id') is not None:
        utilisateur_connecte = get_object_or_404(Utilisateur, id=request.session['utilisateur_id'])

    if request.method == 'POST':
        form = VendreForm(request.POST)
        images = request.FILES.getlist('images')

        # Nouvelle logique de validation pour les images
        # Si c'est une création initiale et qu'il n'y a pas d'images, on affiche une erreur
        if not publication_id and not images:
            messages.error(request, 'Veuillez télécharger entre 3 et 4 images pour la galerie.')
            return render(request, 'ajouter_vente.html', {'form': form, 'bien': bien, 'images_existantes': images_existantes, 'titre_foncier_existant': titre_foncier_existant})

        # Si des images sont uploadées, on s'assure qu'il y en a entre 3 et 4
        if images and not (3 <= len(images) <= 4):
            messages.error(request, 'Veuillez télécharger entre 3 et 4 images.')
            return render(request, 'ajouter_vente.html', {'form': form, 'bien': bien, 'images_existantes': images_existantes, 'titre_foncier_existant': titre_foncier_existant})

        if form.is_valid():
            if instance_vente:
                # Mise à jour manuelle de l'instance Vendre existante
                vente_sauvegardee = instance_vente
                vente_sauvegardee.etat_bien = form.cleaned_data['etat_bien']
                vente_sauvegardee.type_bien = form.cleaned_data['type_bien']
                vente_sauvegardee.localisation = form.cleaned_data['localisation']
                vente_sauvegardee.prix_vente = form.cleaned_data['prix_vente']
                vente_sauvegardee.superficie = form.cleaned_data['superficie']
                vente_sauvegardee.description = form.cleaned_data['description']
                vente_sauvegardee.titre_foncier = form.cleaned_data['titre_foncier']
                vente_sauvegardee.numero_titre_foncier = form.cleaned_data['numero_titre_foncier']
                vente_sauvegardee.statut = 'en_attente'
                vente_sauvegardee.message_de_refus = None
            else:
                # Création d'une nouvelle instance
                proprietaire_obj = get_object_or_404(Utilisateur, id=form.cleaned_data['proprietaire_id'])
                vente_sauvegardee = Vendre.objects.create(
                    type_bien=bien.type, # Correction: bien.type et non bien
                    localisation=bien.localisation,
                    proprietaire=proprietaire_obj,
                    prix_vente=form.cleaned_data['prix_vente'],
                    superficie=form.cleaned_data['superficie'],
                    description=form.cleaned_data['description'],
                    etat_bien=bien.etat,
                    titre_foncier=form.cleaned_data['titre_foncier'],
                    numero_titre_foncier=form.cleaned_data['numero_titre_foncier'],
                    statut='en_attente'
                )

            vente_sauvegardee.save()

            # Mise à jour des images
            if images: # On supprime et on ajoute de nouvelles images uniquement si de nouvelles ont été fournies
                ImageBien.objects.filter(bien_vente=vente_sauvegardee).delete()
            
                for image in images:
                    ImageBien.objects.create(bien_vente=vente_sauvegardee, image=image) 
            
            # La mise à jour de bien.statut ne s'applique qu'à la création initiale
            if not publication_id:
                bien.statut = 'valide'
                bien.save()

            messages.success(request, 'Votre bien a été mis en vente et est en attente de validation!')
            return redirect('publication_attente', publication_id=vente_sauvegardee.id, type_publication='vente')
        else:
            print("Formulaire Vendre invalide :", form.errors)
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        # Initialisation du formulaire
        if instance_vente:
            initial_data = {
                'etat_bien': instance_vente.etat_bien,
                'type_bien': instance_vente.type_bien,
                'localisation': instance_vente.localisation,
                'prix_vente': instance_vente.prix_vente,
                'superficie': instance_vente.superficie,
                'description': instance_vente.description,
                'titre_foncier': instance_vente.titre_foncier,
                'numero_titre_foncier': instance_vente.numero_titre_foncier,
            }
        else:
            initial_data = {}
        
        if utilisateur_connecte and utilisateur_connecte.role == 'proprietaire':
            initial_data['proprietaire_nom'] = f"{utilisateur_connecte.nom} {utilisateur_connecte.prenom}"
            initial_data['proprietaire_id'] = utilisateur_connecte.id
        
        form = VendreForm(initial=initial_data)

    return render(request, 'ajouter_vente.html', {'form': form, 'bien': bien, 'images_existantes': images_existantes, 'titre_foncier_existant': titre_foncier_existant})

def ajouter_location(request, publication_id=None):
    images_existantes = None
    # Mode Modification
    if publication_id:
        instance_location = get_object_or_404(Louer, id=publication_id)
        bien = None
        images_existantes = ImageBien.objects.filter(bien_location=instance_location)
    # Mode Création
    else:
        bien_id = request.GET.get('bien_id') 
        if not bien_id:
            messages.error(request, "ID de bien initial manquant.")
            return redirect('listebien')
        bien = get_object_or_404(Bien, id=bien_id)
        instance_location = None

    utilisateur_connecte = None
    if request.session.get('utilisateur_id') is not None:
        utilisateur_connecte = get_object_or_404(Utilisateur, id=request.session['utilisateur_id'])

    if request.method == 'POST':
        form = LouerForm(request.POST)
        images = request.FILES.getlist('images')

        # Nouvelle logique de validation pour les images
        # Si c'est une création initiale et qu'il n'y a pas d'images, on affiche une erreur
        if not publication_id and not images:
            messages.error(request, 'Veuillez télécharger entre 1 et 4 images pour la galerie.')
            return render(request, 'ajouter_location.html', {'form': form, 'bien': bien, 'images_existantes': images_existantes})

        # Si des images sont uploadées, on s'assure qu'il y en a entre 1 et 4
        if images and not (1 <= len(images) <= 4):
            messages.error(request, 'Veuillez télécharger entre 1 et 4 images.')
            return render(request, 'ajouter_location.html', {'form': form, 'bien': bien, 'images_existantes': images_existantes})

        if form.is_valid():
            if instance_location:
                location_sauvegardee = instance_location
                location_sauvegardee.type_bien = form.cleaned_data['type_bien']
                location_sauvegardee.localisation = form.cleaned_data['localisation']
                location_sauvegardee.loyer_mensuel = form.cleaned_data['loyer_mensuel']
                location_sauvegardee.durée_location = form.cleaned_data['durée_location']
                location_sauvegardee.avance = form.cleaned_data['avance']
                location_sauvegardee.description = form.cleaned_data['description']
                location_sauvegardee.statut = 'en_attente'
                location_sauvegardee.message_de_refus = None
            else:
                proprietaire_obj = get_object_or_404(Utilisateur, id=form.cleaned_data['proprietaire_id'])
                location_sauvegardee = Louer.objects.create(
                    type_bien=bien.type,
                    localisation=bien.localisation,
                    proprietaire=proprietaire_obj,
                    loyer_mensuel=form.cleaned_data['loyer_mensuel'],
                    durée_location=form.cleaned_data['durée_location'],
                    avance=form.cleaned_data['avance'],
                    description=form.cleaned_data['description'],
                    statut='en_attente'
                )
            
            location_sauvegardee.save()

            # Mise à jour des images
            if images: # On supprime et on ajoute de nouvelles images uniquement si de nouvelles ont été fournies
                ImageBien.objects.filter(bien_location=location_sauvegardee).delete()
            
                for image in images:
                    ImageBien.objects.create(bien_location=location_sauvegardee, image=image) 
            
            # La mise à jour de bien.statut ne s'applique qu'à la création initiale
            if not publication_id:
                bien.statut = 'disponible'
                bien.save()

            messages.success(request, 'Votre bien a été mis en location et est en attente de validation!')
            return redirect('publication_attente', publication_id=location_sauvegardee.id, type_publication='location')
        else:
            print("Formulaire Louer invalide :", form.errors)
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        # Initialisation du formulaire
        if instance_location:
            initial_data = {
                'type_bien': instance_location.type_bien,
                'localisation': instance_location.localisation,
                'loyer_mensuel': instance_location.loyer_mensuel,
                'durée_location': instance_location.durée_location,
                'avance': instance_location.avance,
                'description': instance_location.description,
            }
        else:
            initial_data = {}
        
        if utilisateur_connecte and utilisateur_connecte.role == 'proprietaire':
            initial_data['proprietaire_nom'] = f"{utilisateur_connecte.nom} {utilisateur_connecte.prenom}"
            initial_data['proprietaire_id'] = utilisateur_connecte.id
        
        form = LouerForm(initial=initial_data)

    return render(request, 'ajouter_location.html', {'form': form, 'bien': bien, 'images_existantes': images_existantes})

def valider_publications(request):
     # Afficher les biens en attente
    biens_vente_a_valider = Vendre.objects.filter(statut='en_attente')
    biens_location_a_valider = Louer.objects.filter(statut='en_attente')

    if request.method == 'POST':
        bien_id = request.POST.get('bien_id')
        bien_type = request.POST.get('bien_type')
        action = request.POST.get('action') # 'valider' ou 'refuser'

        if bien_type == 'vente':
            bien = get_object_or_404(Vendre, pk=bien_id)
        elif bien_type == 'location':
            bien = get_object_or_404(Louer, pk=bien_id)
        else:
            messages.error(request, "Type de bien invalide.")
            return redirect('valider_publications')

        if action == 'valider':
            bien.statut = 'disponible' # Le bien est maintenant 'publie'
            messages.success(request, f"Le bien de type {bien_type} (ID: {bien_id}) a été validé et publié.")
        elif action == 'refuser':
            bien.statut = 'refuse' # Le bien est 'refuse'
            messages.info(request, f"Le bien de type {bien_type} (ID: {bien_id}) a été refusé.")
        
        bien.save()
        return redirect('valider_publications') # Recharger la page pour voir les changements

    return render(request, 'Valider_publication.html', {
        'publications_vente': biens_vente_a_valider,
        'publications_location': biens_location_a_valider
    })

def refuser_publication(request, bien_type, bien_id):
    if bien_type == 'vente':
        bien = get_object_or_404(Vendre, pk=bien_id)
    elif bien_type == 'location':
        bien = get_object_or_404(Louer, pk=bien_id)
    else:
        messages.error(request, "Type de bien invalide.")
        return redirect('valider_publication')

    if request.method == 'POST':
        message_admin = request.POST.get('message_refus')
        if not message_admin:
            messages.error(request, "Le message de refus ne peut pas être vide.")
            return redirect('refuser_publication', bien_type=bien_type, bien_id=bien_id)
        
        # On ne vérifie plus le message de refus pour éviter les doublons car le propriétaire a la possibilité
        # de ne rien changer et de republier. 
        # La seule chose qui compte c'est que l'admin a pris une décision de refus.
        # on peut donc retirer cette partie:
        # if bien.statut == 'refuse' and bien.message_de_refus == message_admin:
        #     messages.info(request, "Le bien a déjà été refusé avec ce message. Aucune action supplémentaire n'a été effectuée.")
        #     return redirect('valider_publication')
            
        # Mettre à jour le statut, le message et le compteur de refus
        bien.statut = 'refuse'
        bien.message_de_refus = message_admin
        bien.nombre_de_refus += 1
        bien.save()

        if bien.nombre_de_refus >= 3:
            messages.warning(request, f"Le bien de type {bien_type} (ID: {bien_id}) a atteint 3 refus. Il ne peut plus être publié.")
        else:
            messages.success(request, f"Le bien de type {bien_type} (ID: {bien_id}) a été refusé. Le propriétaire a été notifié.")
        
        # Rediriger vers la vue du propriétaire
        return redirect('valider_publication')

    # Cette partie s'exécute pour afficher le formulaire de refus
    return render(request, 'refus_publication.html', {
        'bien': bien,
        'bien_type': bien_type
    })

def confirmer_validation(request, type_publication, publication_id):
    if type_publication == 'vente':
        publication = get_object_or_404(Vendre, id=publication_id)
        # S'assurer que le bien n'a pas atteint la limite de refus
        if publication.nombre_de_refus >= 3:
            messages.error(request, "Ce bien a été refusé 3 fois et ne peut plus être publié.")
            return redirect('valider_publications')
        publication.statut = 'disponible' 
    elif type_publication == 'location':
        publication = get_object_or_404(Louer, id=publication_id)
        # S'assurer que le bien n'a pas atteint la limite de refus
        if publication.nombre_de_refus >= 3:
            messages.error(request, "Ce bien a été refusé 3 fois et ne peut plus être publié.")
            return redirect('valider_publications')
        publication.statut = 'disponible' 
    else:
        from django.http import Http404
        raise Http404("Type de publication inconnu.")
        
    # NOUVELLE LOGIQUE: Réinitialiser le compteur et le message de refus
    publication.nombre_de_refus = 0
    publication.message_de_refus = None # ou une chaîne vide ''
    
    publication.save()
    messages.success(request, "La publication a été validée avec succès.")
    return redirect('valider_publications')

def liste_biens_valides(request):
    vente_valides = Vendre.objects.filter(statut='valide')
    location_valides = Louer.objects.filter(statut='disponible')

    return render(request, 'Bienvalidés.html', {'vente_valides' : vente_valides , 'location_valides': location_valides})

@admin_required
def DashboardAdmin(request):
     # Vérification d'autorisation (la logique que nous avons déjà établie)
    admin_id = request.session.get('admin_id')
    if not admin_id:
        messages.error(request, "Veuillez vous connecter pour accéder à cette page.")
        return redirect('admin_login')
        
    # Récupérer les données statistiques
    total_biens = Bien.objects.filter(statut="enregistré").count()
    publications_en_attente = Vendre.objects.filter(statut="en_attente").count() + Louer.objects.filter(statut="en_attente").count() # Compter les ventes et locations non validées
    biens_valides = Vendre.objects.filter(statut="valide").count() + Louer.objects.filter(statut="disponible").count() # Compter les ventes et locations validées
    total_transactions = Transaction.objects.count() # Supposez que vous avez un modèle de transaction

    context = {
        'total_biens': total_biens,
        'publications_en_attente': publications_en_attente,
        'biens_valides': biens_valides,
        'total_transactions': total_transactions,
    }

    return render(request, 'adminDashboard.html', context)


def publication_attente(request, type_publication, publication_id):
    # Determine quel modèle (Vendre ou Louer) récupérer
    if type_publication == 'vente':
        publication = get_object_or_404(Vendre, id=publication_id)
    elif type_publication == 'location':
        publication = get_object_or_404(Louer, id=publication_id)
    else:
        raise Http404("Type de publication inconnu.")

    # Vérifie si le statut de la publication a été mis à jour par l'administrateur
    # 'valide' pour Vendre, 'disponible' pour Louer
    if (type_publication == 'vente' and publication.statut == 'valide') or \
       (type_publication == 'location' and publication.statut == 'disponible'):
        # Si c'est validé, rediriger vers la page de succès
        return redirect('publication_validee', type_publication=type_publication, publication_id=publication.id)
    
    # 🚨 NOUVEAU : Si le statut est 'refuse', rediriger vers la nouvelle vue de refus
    elif publication.statut == 'refuse':
        return redirect('publication_refusee', type_publication=type_publication, publication_id=publication.id)
    
    # Si le statut n'est pas encore 'valide', 'disponible' ou 'refuse', afficher la page d'attente
    return render(request, 'publication_attente.html', {'publication': publication, 'type_publication': type_publication})


def publication_valides(request, type_publication, publication_id):
    # Récupère l'objet pour l'afficher sur la page de succès
    if type_publication == 'vente':
        publication = get_object_or_404(Vendre, id=publication_id)
    elif type_publication == 'location':
        publication = get_object_or_404(Louer, id=publication_id)
    else:
        raise Http404("Type de publication inconnu.")

    return render(request, 'publication_validee.html', {'publication': publication, 'type_publication': type_publication})

def publication_refusee(request, type_publication, publication_id):
    # Récupère l'objet pour l'afficher sur la page de refus
    if type_publication == 'vente':
        publication = get_object_or_404(Vendre, id=publication_id)
    elif type_publication == 'location':
        publication = get_object_or_404(Louer, id=publication_id)
    else:
        from django.http import Http404
        raise Http404("Type de publication inconnu.")

    return render(request, 'publication_refusee.html', {'publication': publication, 'type_publication': type_publication})

def detail_biens(request, type_bien, pk):
    """
    Vue pour afficher les détails complets d'un bien (vente ou location).
    """
    bien = None
    transaction = None

    if type_bien == 'vendre':
        # Tente de récupérer un bien de type Vendre ou renvoie une erreur 404
        bien = get_object_or_404(Vendre, pk=pk)
    elif type_bien == 'louer':
        bien = get_object_or_404(Louer, pk=pk)
        transaction = Transaction.objects.filter(bien_location=bien).order_by('-date_transaction').first()
    else:
        # Gérer le cas où le type_bien n'est ni 'vendre' ni 'louer'
        # Vous pouvez rediriger, afficher un message d'erreur, etc.
        # Pour l'instant, on peut simplement lever une 404 ou renvoyer sur la liste des biens
        from django.http import Http404
        raise Http404("Type de bien inconnu.")

    context = {
        'bien': bien,
        'transaction': transaction,
    }
    return render(request, 'detailsbien.html', context)


def creer_demande_bien(request, type_bien, bien_id):
    bien = None
    if type_bien == 'vendre':
        bien = get_object_or_404(Vendre, pk=bien_id)
    elif type_bien == 'louer':
        bien = get_object_or_404(Louer, pk=bien_id)
    else:
        messages.error(request, 'Type de bien invalide.')
        return redirect('some_error_page')

    is_renouvellement = request.GET.get('renouvellement') == '1'

    if request.method == 'POST':
        form = DemandeBienForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Vérifier si c'est une demande de renouvellement
            if request.POST.get('is_renouvellement') == 'true':
                # Vérification de l'ancien locataire via les transactions
                ancien_client = Transaction.objects.filter(
                    bien_location=bien,
                    client__email=data['email'],
                    client__nom_complet=data['nom_complet']
                ).exists()

                if not ancien_client:
                    messages.error(request, "Vous ne pouvez pas renouveler cette location car aucune location précédente n'a été trouvée avec vos informations.")
                    return redirect('page_erreur_renouvellement')

                type_demande_value = 'renouvellement'
            else:
                type_demande_value = type_bien

            # Créer la demande
            demande_bien = DemandeBien(
                nom_complet = data['nom_complet'],
                email = data['email'],
                telephone = data['telephone'],
                message = data['message'],
                duree_location_mois = data.get('duree_location_mois'),
                type_demande = type_demande_value,
                bien_vente = bien if type_bien == 'vendre' else None,
                bien_location = bien if type_bien == 'louer' else None,
            )
            demande_bien.save()

            messages.success(request, 'Votre demande a été envoyée avec succès.')
            return redirect('demande_en_attente')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = DemandeBienForm()

    context = {
        'form': form,
        'bien': bien,
        'type_bien': type_bien,
        'is_renouvellement': is_renouvellement,
    }
    return render(request, 'demandebien.html', context)

def is_proprietaire(user):
    # Adaptez cette logique à votre modèle Utilisateur
    # Par exemple, si vous avez un champ 'role' ou si is_staff suffit
    return user.is_authenticated and (user.is_staff or getattr(user, 'role', '') == 'proprietaire')


def supprimer_demande_bien(request, demande_id):
    # La suppression n'a lieu que si la requête est de type POST
    if request.method == 'POST':
        utilisateur_id = request.session.get('utilisateur_id', None)
        if not utilisateur_id:
            messages.error(request, "Vous devez être connecté pour effectuer cette action.")
            return redirect('connexion')

        proprietaire_obj = get_object_or_404(Utilisateur, pk=utilisateur_id)
        demande = get_object_or_404(DemandeBien, pk=demande_id)
        
        is_proprietaire_of_bien = False
        if demande.bien_location and demande.bien_location.proprietaire == proprietaire_obj:
            is_proprietaire_of_bien = True
        elif demande.bien_vente and demande.bien_vente.proprietaire == proprietaire_obj:
            is_proprietaire_of_bien = True

        if not is_proprietaire_of_bien:
            messages.error(request, "Vous n'êtes pas autorisé à effectuer cette action.")
            return redirect('liste_demandes_proprietaire')
        
        # L'action de suppression est ici
        demande.delete()
        messages.success(request, "La demande a été annulée avec succès.")
        return redirect('liste_demandes_proprietaire')
    
    # Si la méthode n'est pas POST, on redirige pour éviter une suppression directe via l'URL
    return redirect('liste_demandes_proprietaire')

def confirmer_suppression_demande(request, demande_id):
    utilisateur_id = request.session.get('utilisateur_id', None)
    if not utilisateur_id:
        messages.error(request, "Vous devez être connecté pour effectuer cette action.")
        return redirect('connexion')

    proprietaire_obj = get_object_or_404(Utilisateur, pk=utilisateur_id)
    demande = get_object_or_404(DemandeBien, pk=demande_id)
    
    is_proprietaire_of_bien = False
    if demande.bien_location and demande.bien_location.proprietaire == proprietaire_obj:
        is_proprietaire_of_bien = True
    elif demande.bien_vente and demande.bien_vente.proprietaire == proprietaire_obj:
        is_proprietaire_of_bien = True

    if not is_proprietaire_of_bien:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette demande.")
        return redirect('liste_demandes_proprietaire')
        
    context = {
        'demande': demande
    }
    # Cette vue affiche simplement la page de confirmation
    return render(request, 'confirmer_suppression_demande.html', context)

def liste_demandes_proprietaire(request):
    utilisateur_id = request.session.get('utilisateur_id', None)
    if not utilisateur_id:
        messages.error(request, "Vous devez être connecté pour voir cette page.")
        return redirect('connexion')

    proprietaire_obj = get_object_or_404(Utilisateur, pk=utilisateur_id)

    demandes_vente = DemandeBien.objects.filter(
        bien_vente__proprietaire=proprietaire_obj
    ).exclude(est_traitee=True)

    demandes_location = DemandeBien.objects.filter(
        bien_location__proprietaire=proprietaire_obj
    ).exclude(est_traitee=True)

    toutes_les_demandes = list(demandes_vente) + list(demandes_location)
    toutes_les_demandes.sort(key=lambda x: x.date_demande, reverse=True)

    context = {
        "demandes": toutes_les_demandes,
        "proprietaire_id": utilisateur_id,
    }
    return render(request, 'proprietaire_demande.html', context)




def marquer_demande_traitee(request, pk):
    if request.method == 'POST':
        utilisateur_id = request.session.get('utilisateur_id')
        if not utilisateur_id:
            messages.error(request, "Erreur d'authentification.")
            return redirect('connexion')

        proprietaire_concerne = get_object_or_404(Utilisateur, pk=utilisateur_id)

        demande = DemandeBien.objects.filter(pk=pk).first()
        renouvellement = RenouvelerLocation.objects.filter(pk=pk).first()

        if not demande and not renouvellement:
            messages.error(request, "Demande introuvable.")
            return redirect('liste_demandes_proprietaire')

        try:
            with db_transaction.atomic():
                if demande:
                    if demande.est_traitee:
                        messages.warning(request, "Cette demande a déjà été traitée.")
                        return redirect('liste_demandes_proprietaire')

                    if demande.bien_vente:
                        # Cas d'une demande de VENTE
                        bien = demande.bien_vente
                        if bien.proprietaire != proprietaire_concerne:
                            messages.error(request, "Vous n'êtes pas autorisé à traiter cette demande de vente.")
                            return redirect('liste_demandes_proprietaire')
                        
                        # Ici, on ne fait que rediriger vers la soumission de documents.
                        # La transaction sera créée lors de la validation des documents.
                        messages.info(request, "Veuillez soumettre les documents de vente pour finaliser la transaction.")
                        return redirect('soumettre_documents_vente', demande_pk=demande.pk)

                    elif demande.bien_location:
                        # Cas d'une demande de LOCATION
                        bien = demande.bien_location
                        if bien.proprietaire != proprietaire_concerne:
                            messages.error(request, "Vous n'êtes pas autorisé à traiter cette demande de location.")
                            return redirect('liste_demandes_proprietaire')

                        # Création de la transaction de location
                        Transaction.objects.create(
                            bien_location=bien,
                            demande=demande,
                            proprietaire=proprietaire_concerne,
                            client_nom=demande.nom_complet,
                            client_email=demande.email,
                            client_telephone=demande.telephone,
                            type_transaction='loue',
                            montant_transaction=bien.loyer_mensuel,
                            date_transaction=timezone.now(),
                            statut_bien_apres_transaction='loue',
                            date_debut_location=timezone.now().date(),
                            date_fin_location=timezone.now().date() + relativedelta(months=demande.duree_location_mois or 1)
                        )
                        
                        # Mettre à jour le statut du bien et de la demande
                        bien.statut = 'loue'
                        bien.save()
                        
                        demande.est_traitee = True
                        demande.date_traitement = timezone.now()
                        demande.save()
                        
                        messages.success(request, f"Le bien '{bien.type_bien}' a été marqué comme LOUÉ. Transaction enregistrée.")
                        return redirect('liste_demandes_proprietaire')

                elif renouvellement:
                    # Cas d'une demande de RENOUVELLEMENT (la logique reste inchangée)
                    if renouvellement.traite:
                        messages.warning(request, "Cette demande de renouvellement a déjà été traitée.")
                        return redirect('liste_demandes_proprietaire')

                    if renouvellement.bien.proprietaire != proprietaire_concerne:
                        messages.error(request, "Vous n'êtes pas autorisé à traiter ce renouvellement.")
                        return redirect('liste_demandes_proprietaire')

                    renouvellement.traite = True
                    renouvellement.save()
                    
                    bien = renouvellement.bien
                    Transaction.objects.create(
                        bien_location=bien,
                        renouvellement=renouvellement,
                        proprietaire=proprietaire_concerne,
                        client_nom=renouvellement.nom_complet,
                        client_email=renouvellement.email,
                        client_telephone=renouvellement.telephone,
                        type_transaction='renouvellement_loue',
                        montant_transaction=bien.loyer_mensuel,
                        date_transaction=timezone.now(),
                        statut_bien_apres_transaction='loue',
                        date_debut_location=timezone.now().date(),
                        date_fin_location=timezone.now().date() + relativedelta(months=renouvellement.duree_nouvelle_location or 1)
                    )
                    messages.success(request, f"Renouvellement accepté pour le bien '{bien.type_bien}'. Transaction enregistrée.")
                    return redirect('liste_demandes_proprietaire')

        except Exception as e:
            messages.error(request, f"Erreur lors du traitement : {e}")
            return redirect('liste_demandes_proprietaire')

    messages.error(request, "Méthode non autorisée.")
    return redirect('liste_demandes_proprietaire')

def demande_en_attente(request):
    """
    Affiche la page d'attente pour un client après qu'il a soumis une demande.
    """
    context = {
        'message_principal': "Votre demande a bien été reçue !",
        'message_secondaire': "Le propriétaire du bien vous contactera prochainement."
    }
    return render(request, 'demande_en_attente.html', context)

def demande_traitee_succes(request):
    """
    Affiche la page de succès après qu'une demande a été traitée (pour l'admin/propriétaire).
    """
    context = {
        'message_principal': "La demande a été marquée comme traitée avec succès !",
        'message_secondaire': "Les informations ont été mises à jour."
    }
    # Correction du nom de template pour correspondre à nos instructions précédentes
    return render(request, 'demande_traitee.html', context)

def liste_transactions(request):
   

    transactions = Transaction.objects.all().order_by('-date_transaction') # Récupère toutes les transactions

    context = {
        'transactions': transactions,
    }
    return render(request, 'liste_transactions.html', context) # Nom du template à créer


def page_erreur(request, message="Une erreur inattendue est survenue."):
    """
    Vue générique pour afficher un message d'erreur.
    """
    context = {
        'error_message': message,
        'home_url_name': 'property', # Le nom de votre URL pour la page d'accueil
    }
    return render(request, 'error_page.html', context)

def renouveler_location(request, bien_id):
    bien = get_object_or_404(Louer, pk=bien_id)

    if request.method == 'POST':
        form = RenouvelerLocationForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom_complet']
            email = form.cleaned_data['email']

            # Vérifie que le client a déjà loué ce bien
            deja_client = Transaction.objects.filter(
                bien_location=bien,
                nom_complet=nom,
                email=email
            ).exists()

            if not deja_client:
                messages.error(request, "Vous n'avez jamais loué ce bien. Requête rejetée.")
            else:
                renouvellement = form.save(commit=False)
                renouvellement.bien = bien
                renouvellement.save()
                messages.success(request, "Votre demande de renouvellement a été envoyée au propriétaire.")
            return redirect('detail_biens', type_bien='louer', pk=bien.pk)
    else:
        form = RenouvelerLocationForm()

    return render(request, 'renouvellement_location.html', {
        'form': form,
        'bien': bien
    })

def modifier_vente(request, vente_id):
    # Étape 1 : Récupérer les objets Vendre et Bien
    vente = get_object_or_404(Vendre, id=vente_id)
    
    # Étape 2 : Récupérer l'objet Bien associé à la vente
    # On utilise le modèle ImageBien comme pont, car il est lié à la fois à Vendre et à Bien.
    try:
        # On trouve la première image liée à cette vente
        premiere_image = vente.images.first() 
        if premiere_image:
            # On récupère l'objet Bien via cette image
            bien_associe = premiere_image.bien
        else:
            # Si aucune image n'est trouvée, c'est un cas d'erreur
            messages.error(request, "Impossible de trouver le bien associé à cette vente.")
            return redirect('bienpublies')
    except AttributeError:
        # Gérer le cas où vente.images n'existe pas (si la relation est différente)
        messages.error(request, "Erreur lors de la récupération des images. Contactez l'administrateur.")
        return redirect('bienpublies')

    # Étape 3 : Vérifier les autorisations de l'utilisateur
    utilisateur_id = request.session.get('utilisateur_id')
    if not utilisateur_id or vente.proprietaire.id != utilisateur_id:
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce bien.")
        return redirect('bienpublies')

    if request.method == 'POST':
        venteform = VendreForm(request.POST, request.FILES)

        if venteform.is_valid():
            # Étape 4 : Mettre à jour les champs de la vente
            vente.type_bien = venteform.cleaned_data['type_bien']
            vente.prix_vente = venteform.cleaned_data['prix_vente']
            vente.superficie = venteform.cleaned_data['superficie']
            vente.description = venteform.cleaned_data['description']
            vente.localisation = venteform.cleaned_data['localisation']
            vente.etat_bien = venteform.cleaned_data['etat_bien']
            vente.numero_titre_foncier = venteform.cleaned_data['numero_titre_foncier']

            # Étape 5 : Gérer la suppression des images
            images_a_supprimer_ids = request.POST.getlist('images_a_supprimer')
            for image_id in images_a_supprimer_ids:
                try:
                    # On s'assure que l'image appartient bien à cette vente avant de la supprimer
                    ImageBien.objects.get(pk=image_id, bien_vente=vente).delete()
                except ImageBien.DoesNotExist:
                    pass

            # Étape 6 : Gérer l'ajout de nouvelles images
            images_a_ajouter = request.FILES.getlist('images_a_ajouter')
            nombre_images_restantes = vente.images.count()
            
            if (nombre_images_restantes + len(images_a_ajouter)) > 4:
                messages.error(request, 'Le nombre total d\'images ne peut pas dépasser 4.')
                return render(request, "modifier_vente.html", {"form": venteform, "vente": vente, "bien_associe": bien_associe})

            for image_file in images_a_ajouter:
                # La ligne de correction : on utilise le "bien_associe" pour créer la nouvelle image
                ImageBien.objects.create(bien_vente=vente, bien=bien_associe, image=image_file)
            
            # Étape 7 : Gérer le titre foncier et la sauvegarde
            if 'titre_foncier' in request.FILES:
                vente.titre_foncier = request.FILES['titre_foncier']
            
            vente.save()
            
            # Étape 8 : Mettre à jour le statut du bien associé
            # Le statut est 'valide' car la vente est en cours de modification
            bien_associe.statut = 'valide'
            bien_associe.save()

            messages.success(request, 'La vente a été modifiée avec succès!')
            return redirect('bienpublies')
        else:
            # En cas d'erreurs de formulaire
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
            return render(request, 'modifier_vente.html', {'form': venteform, 'vente': vente})
    else:
        # Affichage du formulaire initial
        venteform = VendreForm(initial={
            'type_bien': vente.type_bien,
            'prix_vente': vente.prix_vente,
            'superficie': vente.superficie,
            'localisation': vente.localisation,
            'description': vente.description,
            'etat_bien': vente.etat_bien,
            'numero_titre_foncier': vente.numero_titre_foncier,
        })
        
    return render(request, 'modifier_vente.html', {'form': venteform, 'vente': vente, 'bien_associe': bien_associe})

def modifier_location(request, location_id):
    # Étape 1 : Récupérer l'objet Louer
    location = get_object_or_404(Louer, id=location_id)
    
    # Étape 2 : Récupérer l'objet Bien associé à la location
    # On utilise le modèle ImageBien comme pont, car il est lié à la fois à Louer et à Bien.
    try:
        premiere_image = location.images.first() 
        if premiere_image:
            bien_associe = premiere_image.bien
        else:
            messages.error(request, "Impossible de trouver le bien associé à cette location.")
            return redirect('bienpublies')
    except AttributeError:
        messages.error(request, "Erreur lors de la récupération des images. Contactez l'administrateur.")
        return redirect('bienpublies')

    # Étape 3 : Vérifier les autorisations de l'utilisateur
    utilisateur_id = request.session.get('utilisateur_id')
    if not utilisateur_id or location.proprietaire.id != utilisateur_id:
        messages.error(request, "Vous n'êtes pas autorisé à modifier ce bien.")
        return redirect('bienpublies')

    if request.method == 'POST':
        louerform = LouerForm(request.POST, request.FILES)

        if louerform.is_valid():
            # Étape 4 : Mettre à jour les champs de la location
            location.type_bien = louerform.cleaned_data['type_bien']
            location.loyer_mensuel = louerform.cleaned_data['loyer_mensuel']
            location.durée_location = louerform.cleaned_data['durée_location']
            location.avance = louerform.cleaned_data['avance']
            location.localisation = louerform.cleaned_data['localisation']
            location.description = louerform.cleaned_data['description']
            
            # Étape 5 : Gérer la suppression des images
            images_a_supprimer_ids = request.POST.getlist('images_a_supprimer')
            for image_id in images_a_supprimer_ids:
                try:
                    ImageBien.objects.get(pk=image_id, bien_location=location).delete()
                except ImageBien.DoesNotExist:
                    pass

            # Étape 6 : Gérer l'ajout de nouvelles images
            images_a_ajouter = request.FILES.getlist('images_a_ajouter')
            nombre_images_restantes = location.images.count()
            
            if (nombre_images_restantes + len(images_a_ajouter)) > 4:
                messages.error(request, 'Le nombre total d\'images ne peut pas dépasser 4.')
                return render(request, "modifier_location.html", {"form": louerform, "location": location})

            # Ligne de correction : on passe l'objet `bien_associe` au lieu de `location.bien`
            for image_file in images_a_ajouter:
                ImageBien.objects.create(bien_location=location, bien=bien_associe, image=image_file)

            # Étape 7 : Mettre à jour et sauvegarder
            location.save()

            # Mettre à jour le statut du bien associé
            bien_associe.statut = 'valide'
            bien_associe.save()
            
            messages.success(request, 'La location a été modifiée avec succès!')
            return redirect('bienpublies')
        else:
            print("Formulaire invalide ", louerform.errors)
            messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
            return render(request, 'modifier_location.html', {'form': louerform, 'location': location})
    else:
        # Affichage du formulaire initial
        louerform = LouerForm(initial={
            'type_bien': location.type_bien,
            'loyer_mensuel': location.loyer_mensuel,
            'durée_location': location.durée_location,
            'avance': location.avance,
            'localisation': location.localisation,
            'description': location.description,
            'proprietaire_nom': f"{location.proprietaire.nom} {location.proprietaire.prenom}",
            'proprietaire_id': location.proprietaire.id,
        })
        
    return render(request, 'modifier_location.html', {'form': louerform, 'location': location, 'bien_associe': bien_associe})

def supprimer_vente(request, vente_id):
    vente = get_object_or_404(Vendre, id=vente_id)
    
    utilisateur_id = request.session.get('utilisateur_id')
    
    if not utilisateur_id or vente.proprietaire.id != utilisateur_id:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette publication.")
        return redirect('bienpublies')

    if request.method == 'POST':
        vente.delete()
        messages.success(request, "La vente a été supprimée avec succès.")
        return redirect('bienpublies')
    
    # Rendre une page de confirmation pour la requête GET
    return render(request, "confirmer_suppression_vente.html", {"vente": vente})

def supprimer_location(request, location_id):
    location = get_object_or_404(Louer, id=location_id)
    
    utilisateur_id = request.session.get('utilisateur_id')
    
    if not utilisateur_id or location.proprietaire.id != utilisateur_id:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette publication.")
        return redirect('bienpublies')

    if request.method == 'POST':
        location.delete()
        messages.success(request, "La location a été supprimée avec succès.")
        return redirect('bienpublies')
    
    # Rendre une page de confirmation pour la requête GET
    return render(request, "confirmer_suppression_location.html", {"location": location})

def soumettre_documents_vente(request, demande_pk):
    demande = get_object_or_404(DemandeBien, pk=demande_pk)

    if request.method == 'POST':
        form = DocumentsTransactionVenteForm(request.POST, request.FILES)
        if form.is_valid():
            # Création manuelle d'une nouvelle instance du modèle
            # On utilise form.cleaned_data pour récupérer les valeurs
            # soumises par le formulaire.
            documents = DocumentsTransactionVente.objects.create(
                demande_bien=demande,
                bien_vente=demande.bien_vente,
                proprietaire=demande.bien_vente.proprietaire,
                
                # Les champs du formulaire Forms.py
                recu_vente=form.cleaned_data.get('recu_vente'),
                copie_attestation_mandataire=form.cleaned_data.get('copie_attestation_mandataire'),
                copie_attestations_heritage=form.cleaned_data.get('copie_attestations_heritage'),
                nouveau_titre_foncier=form.cleaned_data.get('nouveau_titre_foncier'),
                
                nom_temoin1_proprietaire=form.cleaned_data.get('nom_temoin1_proprietaire'),
                temoin1_proprietaire_cni_recto=form.cleaned_data.get('temoin1_proprietaire_cni_recto'),
                temoin1_proprietaire_cni_verso=form.cleaned_data.get('temoin1_proprietaire_cni_verso'),
                
                nom_temoin1_client=form.cleaned_data.get('nom_temoin1_client'),
                temoin1_client_cni_recto=form.cleaned_data.get('temoin1_client_cni_recto'),
                temoin1_client_cni_verso=form.cleaned_data.get('temoin1_client_cni_verso'),
                
                nom_temoin2_proprietaire=form.cleaned_data.get('nom_temoin2_proprietaire'),
                temoin2_proprietaire_cni_recto=form.cleaned_data.get('temoin2_proprietaire_cni_recto'),
                temoin2_proprietaire_cni_verso=form.cleaned_data.get('temoin2_proprietaire_cni_verso'),
                
                nom_temoin2_client=form.cleaned_data.get('nom_temoin2_client'),
                temoin2_client_cni_recto=form.cleaned_data.get('temoin2_client_cni_recto'),
                temoin2_client_cni_verso=form.cleaned_data.get('temoin2_client_cni_verso'),
                
                nom_temoin3_proprietaire=form.cleaned_data.get('nom_temoin3_proprietaire'),
                temoin3_proprietaire_cni_recto=form.cleaned_data.get('temoin3_proprietaire_cni_recto'),
                temoin3_proprietaire_cni_verso=form.cleaned_data.get('temoin3_proprietaire_cni_verso'),
                
                nom_temoin3_client=form.cleaned_data.get('nom_temoin3_client'),
                temoin3_client_cni_recto=form.cleaned_data.get('temoin3_client_cni_recto'),
                temoin3_client_cni_verso=form.cleaned_data.get('temoin3_client_cni_verso'),
                
                # Le statut initial est False par défaut, mais il est bon de le confirmer explicitement
                valide_par_admin=False,
            )

            messages.success(request, 'Vos documents ont été soumis avec succès et sont en attente de validation.')
            return redirect('liste_demandes_proprietaire')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = DocumentsTransactionVenteForm()

    context = {
        'form': form,
        'demande': demande,
    }
    return render(request, 'soumettre_documents_vente.html', context)


# --- Les vues suivantes ne sont plus protégées ---
def liste_documents_a_valider(request):
    """
    Cette vue affiche la liste des documents en attente de validation.
    """
    documents_en_attente = DocumentsTransactionVente.objects.filter(valide_par_admin=False).order_by('-date_soumission')

    context = {
        'documents_en_attente': documents_en_attente,
    }
    return render(request, 'liste_documents_a_valider.html', context)

def valider_document(request, pk):
    """
    Cette vue valide un document et déclenche la création d'une transaction.
    """
    if request.method == 'POST':
        document = get_object_or_404(DocumentsTransactionVente, pk=pk)

        # Vérifie si le document n'a pas déjà été validé
        if document.valide_par_admin:
            messages.warning(request, "Ce document a déjà été validé.")
            return redirect('liste_documents_a_valider')

        try:
            # Enregistrement de la transaction et mise à jour des statuts
            with db_transaction.atomic():
                bien = document.bien_vente
                demande = document.demande_bien
                proprietaire = document.proprietaire

                Transaction.objects.create(
                    bien_vente=bien,
                    demande=demande,
                    proprietaire=proprietaire,
                    client_nom=demande.nom_complet,
                    client_email=demande.email,
                    client_telephone=demande.telephone,
                    type_transaction='vendu',
                    montant_transaction=bien.prix_vente,
                    date_transaction=timezone.now(),
                    statut_bien_apres_transaction='vendu',
                )

                bien.statut = 'vendu'
                bien.cloturer = True
                bien.save()

                demande.est_traitee = True
                demande.date_traitement = timezone.now()
                demande.save()

                # Marquer le document comme validé
                document.valide_par_admin = True
                document.date_validation = timezone.now()
                document.save()
            
            messages.success(request, f"Les documents pour la vente du bien '{bien.type_bien}' ont été validés et la transaction a été enregistrée.")
            return redirect('liste_documents_valides')

        except Exception as e:
            messages.error(request, f"Une erreur s'est produite lors de la validation : {e}")
            return redirect('liste_documents_valides')

    messages.error(request, "Méthode non autorisée.")
    return redirect('liste_documents_valides')

# Dans mon_app/views.py

def liste_documents_valides(request):
    """
    Cette vue affiche la liste des documents qui ont été validés.
    """
    documents_valides = DocumentsTransactionVente.objects.filter(valide_par_admin=True).order_by('-date_validation')
    context = {
        'documents_valides': documents_valides,
    }
    return render(request, 'documents_valides.html', context)

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                admin_user = AdminLogin.objects.get(username=username, password=password)
                
                # STOCKAGE DE L'ID DE L'ADMINISTRATEUR DANS LA SESSION
                request.session['admin_id'] = admin_user.id
                
                messages.success(request, 'Connexion réussie !')
                return redirect('dashboard_admin')
            except AdminLogin.DoesNotExist:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = AdminLoginForm()

    return render(request, 'admin_login.html', {'form': form})