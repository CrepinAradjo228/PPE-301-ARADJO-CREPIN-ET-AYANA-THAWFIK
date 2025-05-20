from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render , redirect,get_object_or_404
from .models import Proprietaire,Client,Utilisateur,Bien,Publication
from .forms import UtilisateurForm,ConnexionForm,BienForm,PublierForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password , check_password

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
    if request.method == 'POST':
        form = PublierForm(request.POST, request.FILES, bien=bien)
        if form.is_valid():
            # Ici tu peux enregistrer dans le modèle Publication (si tu en as un)
            Publication.objects.create(
                bien=bien,
                titrefoncier=form.cleaned_data['titrefoncier'],
                carterecto=form.cleaned_data['carterecto'],
                carteverso=form.cleaned_data['carteverso'],
                planbien=form.cleaned_data['planbien'],
                nature_publication=form.cleaned_data['nature_publication'],
                description=form.cleaned_data['description'],
                datepublication = form.cleaned_data['datepublication'],
            )
            return redirect('property')
    else:
        form = PublierForm(bien=bien)

    return render(request, 'publication.html', {'form': form})

def listePublication(request):
        # Récupère toutes les publications avec leurs informations associées sur le bien
    publications = Publication.objects.select_related('bien').all()
    
    context = {
        'listepublications': publications
    }
    
    return render(request, "properties.html", context)
