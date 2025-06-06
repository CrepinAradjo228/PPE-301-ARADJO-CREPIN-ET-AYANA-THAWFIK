from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render , redirect,get_object_or_404
from .models import Proprietaire,Client,Utilisateur,Bien,Publication,Vendre,Louer
from .forms import UtilisateurForm,ConnexionForm,BienForm,PublierForm,VendreForm,LouerForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password , check_password
from django.contrib import messages

def home(request):
    return render(request, 'index.html')
def property(request):
    return render(request , 'properties.html')
def contact(request):
    return render(request , 'contact.html')
def landpage(request):
    return render(request , 'homepage.html')
def service(request):
    return render(request , 'services.html')
def dashboard(request):
    # Vérifie si l'utilisateur est connecté
    if not request.session.get('utilisateur_id'):
        return redirect('connexion')
    # Vérifie si l'utilisateur est bien un propriétaire
    if request.session.get('utilisateur_role') != 'proprietaire':
        return redirect('connexion')  # Ou une page d'erreur/accès refusé
    return render(request, 'Dashboard.html')


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
                    return redirect('home')
                else:
                    return redirect('dashboard')
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
    if request.method == "POST":
        form = BienForm(request.POST, request.FILES)
        if form.is_valid():
            Bien.objects.create(
                nom=form.cleaned_data['nom'],
                type=form.cleaned_data['type'],
                localisation=form.cleaned_data['localisation'],
                prix=form.cleaned_data['prix'],
                etat=form.cleaned_data['etat'],
                image=form.cleaned_data['image'],
            )
            return redirect('listebien')
        else:
            print("Formulaire invalide :", form.errors)
    else:
        form = BienForm()
    return render(request, 'register.html', {'form': form})

def listeBien(request):
    context = {"listebiens":Bien.objects.all() }
    return render(request , "listebien.html" , context)

def PublierBien(request, id):
    bien = get_object_or_404(Bien, id=id)

    # Affiche uniquement la page de choix de type de publication
    return render(request, 'choix_publication.html', {'bien': bien})

def listePublication(request):
    ventes = Vendre.objects.all()
    locations = Louer.objects.all()

    # Fusion des 2 types de publication
    listepublications = list(ventes) + list(locations)

    return render(request, "properties.html", {
        'listepublications': listepublications
    })
    
def choix_publication(request):
    if request.method == 'POST':
        choix = request.POST.get('choix')
        if choix == 'location':
            return redirect('ajouter_location')  # URL vers le formulaire de location
        elif choix == 'vente':
            return redirect('ajouter_vente')     # URL vers le formulaire de vente
    return render(request, 'choix_publication.html')





from django.contrib import messages
from .models import Utilisateur, Vendre

def ajouter_vente(request):
    if request.method == 'POST':
        form = VendreForm(request.POST, request.FILES)
        if form.is_valid():
            vente = Vendre.objects.create(
                type_bien=form.cleaned_data['type_bien'],
                prix_vente=form.cleaned_data['prix_vente'],
                superficie=form.cleaned_data['superficie'],
                localisation=form.cleaned_data['localisation'],
                description=form.cleaned_data['description'],
                etat_bien=form.cleaned_data['etat_bien'],
                image_principale=form.cleaned_data['image_principale'],
                titre_foncier=form.cleaned_data['titre_foncier'],
                numero_titre_foncier=form.cleaned_data['numero_titre_foncier'],
                proprietaire=form.cleaned_data['proprietaire'],
                statut='en_attente'
            )

            proprietaire = form.cleaned_data['proprietaire']

            # Redirection selon le rôle du propriétaire
            if proprietaire.role == 'utilisateur':
                return redirect('publication_attente')  # nom de ta page d’attente
            else:
                return redirect('dashboard_admin')  # nom de ta page d’attente

    else:
        form = VendreForm()

    return render(request, 'ajouter_vente.html', {'form': form})


def ajouter_location(request):
    if request.method == 'POST':
        form = LouerForm(request.POST, request.FILES)
        if form.is_valid():
            Louer.objects.create(
                type_bien=form.cleaned_data['type_bien'],
                loyer_mensuel=form.cleaned_data['loyer_mensuel'],
                durée_location=form.cleaned_data['durée_location'],
                avance=form.cleaned_data['avance'],
                localisation=form.cleaned_data['localisation'],
                description=form.cleaned_data['description'],
                image_principale=form.cleaned_data['image_principale'],
                proprietaire=form.cleaned_data['proprietaire'],
            )
            return redirect('property')  # Redirige vers la page des publications
    else:
        form = LouerForm()

    return render(request, 'ajouter_location.html', {'form': form})

def valider_publications(request):
    biens_a_valider = Vendre.objects.filter(statut='en_attente')
    return render(request, 'Valider_publication.html', {'publications': biens_a_valider})


def confirmer_validation(request, id):
    vente = get_object_or_404(Vendre, id=id)
    vente.statut = 'valide'
    vente.save()

    return render(request, 'publication_validee.html', {'vente': vente})


def liste_biens_valides(request):
    biens_valides = Vendre.objects.filter(statut='valide')
    return render(request, 'Bienvalidés.html', {'biens_valides': biens_valides})

def DashboardAdmin(request):
    return render(request, 'AdminDashboard.html')

def publication_attente(request):
    biens_en_attente = Vendre.objects.filter(statut='en_attente')
    return render(request, 'publication_attente.html', {'biens_en_attente': biens_en_attente})

def publication_validee(request):
    biens_valides = Vendre.objects.filter(statut='valide')
    return render(request, 'publication_validee.html', {'biens_valides': biens_valides})