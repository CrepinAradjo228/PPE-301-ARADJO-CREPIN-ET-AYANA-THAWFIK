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
def about(request):
    return render(request , 'about.html')
def service(request):
    return render(request , 'services.html')
def propertynew(request):
    return render(request , 'Dashboard.html')


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
                    password1=password1,
                    nom=form.cleaned_data['nom'],
                    prenom=form.cleaned_data['prenom'],
                    sexe=form.cleaned_data['sexe'],
                    age=form.cleaned_data['age'],
                    numero=form.cleaned_data['numero'],
                    email=form.cleaned_data['email'],
                    role=form.cleaned_data['role'],
                )
                utilisateur.save()


                # Redirection selon le rôle de l'utilisateur
                if utilisateur.role == 'client':
                    return redirect('home')  # Remplace 'home' par l'URL de la page client
                else:
                    return redirect('property')  # Remplace 'property' par l'URL de la page propriétaire
    else:
        form = UtilisateurForm()
    
    return render(request, 'inscription.html', {'form': form})
  # assure-toi que ton formulaire est bien importé

def connexion_view(request):
    erreur = None

    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username_saisi = form.cleaned_data['username']
            password_saisi = form.cleaned_data['password']
            role_saisi = form.cleaned_data['role']

            utilisateurs = Utilisateur.objects.all()
            utilisateur_trouve = None

            for u in utilisateurs:
                if u.username == username_saisi and u.password1 == password_saisi:
                    utilisateur_trouve = u
                    break

            if utilisateur_trouve:
                if utilisateur_trouve.role != role_saisi:
                    erreur = "Rôle incorrect pour cet utilisateur."
                else:
                    if role_saisi == 'client':
                        return redirect('home')
                    elif role_saisi == 'proprietaire':
                        return redirect('property')
            else:
                erreur = "Nom d'utilisateur ou mot de passe incorrect."
    else:
        form = ConnexionForm()

    return render(request, 'connexion.html', {'form': form, 'erreur': erreur})



def deconnexion_view(request):
    logout(request)
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
    return render(request, 'enregistrer_bien.html', {'form': form})

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
