from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render , redirect,get_object_or_404
from .models import Proprietaire,Client,Utilisateur,Bien,Publication,Vendre,Louer,DemandeBien
from .forms import UtilisateurForm,ConnexionForm,BienForm,PublierForm,VendreForm,LouerForm,DemandeBienForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import make_password , check_password
from django.contrib import messages
from django.views.generic import TemplateView

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
                    return redirect('property')
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
            # Récupérer les données validées du formulaire
            nom = form.cleaned_data['nom']
            type_bien = form.cleaned_data['type'] # J'utilise type_bien pour éviter le conflit avec 'type' fonction built-in
            localisation = form.cleaned_data['localisation']
            prix = form.cleaned_data['prix']
            etat = form.cleaned_data['etat']
            image = form.cleaned_data['image']

            Bien.objects.create(
                nom=nom,
                type=type_bien, # Assurez-vous d'utiliser type_bien ici
                localisation=localisation,
                prix=prix,
                etat=etat,
                image=image,
                statut='enregistre',  # Le statut est défini ici explicitement
            )
            return redirect('listebien')
        else:
            print("Formulaire invalide :", form.errors)
    else:
        form = BienForm()
        
    return render(request, 'register.html', {'form': form})

def listeBien(request):
    listebiens = Bien.objects.filter(statut='enregistre')
    context = {"listebiens": listebiens}
    return render(request, "listebien.html", context)

def PublierBien(request, id):
    bien = get_object_or_404(Bien, id=id)
    request.session['bien_en_publication_id'] = bien.id
    return redirect('choixpublication' ,id=bien.id) 

# Dans IMMOBILIER_APP/views.py
from django.shortcuts import render
from .models import Vendre, Louer # Assurez-vous d'importer vos modèles

def listePublication(request):
    ventes = Vendre.objects.filter(statut='valide')
    locations = Louer.objects.filter(statut='disponible')

    listepublications = []

    # Processus pour les biens en Vente
    for bien_vente in ventes:
        # Assurons-nous que type_bien_str et pk sont toujours disponibles
        # même si cela ne devrait pas être nécessaire avec les @property bien définies.
        # C'est une mesure de sécurité si le problème vient d'ailleurs.
        if not hasattr(bien_vente, 'type_bien_str') or not bien_vente.type_bien_str:
            bien_vente.type_bien_str = 'vendre' # Force la valeur par défaut si elle est manquante

        if not hasattr(bien_vente, 'pk') or not bien_vente.pk:
            # Ceci est critique. Si un bien n'a pas de PK, il y a un problème majeur de base de données.
            # Nous pouvons assigner une PK bidon, mais cela cache un problème.
            # Pour l'instant, nous allons ignorer le bien sans PK valide pour éviter l'erreur.
            print(f"AVERTISSEMENT: Bien en vente sans PK valide, ignoré. Bien: {bien_vente}")
            continue # Passe au bien suivant

        listepublications.append(bien_vente)

    # Processus pour les biens en Location
    for bien_location in locations:
        if not hasattr(bien_location, 'type_bien_str') or not bien_location.type_bien_str:
            bien_location.type_bien_str = 'louer' # Force la valeur par défaut

        if not hasattr(bien_location, 'pk') or not bien_location.pk:
            print(f"AVERTISSEMENT: Bien en location sans PK valide, ignoré. Bien: {bien_location}")
            continue # Passe au bien suivant

        listepublications.append(bien_location)

    # Note: Les print() de débogage des messages précédents peuvent être utiles ici
    # pour voir si des biens sont ignorés ou si les valeurs sont "forcées".

    return render(request, "properties.html", {
        'listepublications': listepublications
    })

    
def choix_publication(request, id): # La signature de la fonction doit accepter l'ID
    bien = get_object_or_404(Bien, id=id) 
    return render(request, 'choix_publication.html', {'bien': bien})

def bienpublies(request):
    listebiens_publies = Bien.objects.filter(statut='publie')
    context = {"listebiens_publies": listebiens_publies}
    return render(request, "bienpublies.html", context)

# votre_app/views.py

def ajouter_vente(request):
    bien_id = request.GET.get('bien_id') 
    if not bien_id:
        return redirect('listebien') 

    bien = get_object_or_404(Bien, id=bien_id) # Récupère l'objet Bien initial

    if request.method == 'POST':
        form = VendreForm(request.POST, request.FILES)
        if form.is_valid():
            proprietaire_selectionne = form.cleaned_data['proprietaire'] 

            nouvelle_vente = Vendre.objects.create(
                type_bien=bien.type, 
                localisation=bien.localisation, 
                image_principale=bien.image, 
                proprietaire=proprietaire_selectionne, 
                prix_vente=form.cleaned_data['prix_vente'],
                superficie=form.cleaned_data['superficie'],
                description=form.cleaned_data['description'],
                etat_bien=bien.etat,
                titre_foncier=form.cleaned_data['titre_foncier'],
                numero_titre_foncier=form.cleaned_data['numero_titre_foncier'],
                statut='en_attente' 
            )

            return redirect('publication_attente', publication_id=nouvelle_vente.id, type_publication='vente')
            
        else:
            print("Formulaire Vendre invalide :", form.errors) 
    else:
        form = VendreForm()

    return render(request, 'ajouter_vente.html', {'form': form, 'bien': bien})

def ajouter_location(request):
    bien_id = request.GET.get('bien_id') 
    if not bien_id:
        return redirect('listebien') 

    bien = get_object_or_404(Bien, id=bien_id)

    if request.method == 'POST':
        form = LouerForm(request.POST, request.FILES)
        if form.is_valid():
            proprietaire_selectionne = form.cleaned_data['proprietaire'] 

            nouvelle_location = Louer.objects.create(
                type_bien=bien.type, 
                localisation=bien.localisation, 
                image_principale=bien.image, 
                proprietaire=proprietaire_selectionne, 
                loyer_mensuel=form.cleaned_data['loyer_mensuel'],
                durée_location=form.cleaned_data['durée_location'],
                avance=form.cleaned_data['avance'],
                description=form.cleaned_data['description'],
                statut='en_attente' 
            )

            return redirect('publication_attente_proprietaire', publication_id=nouvelle_location.id, type_publication='location')
        else:
            print("Formulaire Louer invalide :", form.errors) # Pour le débogage
    else:
        form = LouerForm()

    return render(request, 'ajouter_location.html', {'form': form, 'bien': bien})

def valider_publications(request):
    biens_vente_a_valider = Vendre.objects.filter(statut='en_attente')
    biens_location_a_valider = Louer.objects.filter(statut='en_attente')
    
    return render(request, 'Valider_publication.html', {
        'publications_vente': biens_vente_a_valider,
        'publications_location': biens_location_a_valider
    })



def confirmer_validation(request, type_publication, publication_id):
    if type_publication == 'vente':
        publication = get_object_or_404(Vendre, id=publication_id)
        publication.statut = 'valide' # Statut pour Vendre
    elif type_publication == 'location':
        publication = get_object_or_404(Louer, id=publication_id)
        publication.statut = 'disponible' # Statut pour Louer
    else:
        from django.http import Http404
        raise Http404("Type de publication inconnu.")
        
    publication.save()
    return redirect('valider_publication')

def liste_biens_valides(request):
    biens_valides = Vendre.objects.filter(statut='valide')
    return render(request, 'Bienvalidés.html', {'biens_valides': biens_valides})

def DashboardAdmin(request):
    return render(request, 'AdminDashboard.html')

def publication_attente(request, type_publication, publication_id):
    # Détermine quel modèle (Vendre ou Louer) récupérer
    if type_publication == 'vente':
        publication = get_object_or_404(Vendre, id=publication_id)
    elif type_publication == 'location':
        publication = get_object_or_404(Louer, id=publication_id)
    else:
        from django.http import Http404
        raise Http404("Type de publication inconnu.")

    # Vérifie si le statut de la publication a été mis à jour par l'administrateur
    # 'valide' pour Vendre, 'disponible' pour Louer
    if (type_publication == 'vente' and publication.statut == 'valide') or \
       (type_publication == 'location' and publication.statut == 'disponible'):
        # Si c'est validé, rediriger vers la page de succès
        return redirect('publication_validee', type_publication=type_publication, publication_id=publication.id)
    
    # Si le statut n'est pas encore 'valide'/'disponible', afficher la page d'attente
    return render(request, 'publication_attente.html', {'publication': publication, 'type_publication': type_publication})


def publication_valides(request, type_publication, publication_id):
    # Récupère l'objet pour l'afficher sur la page de succès
    if type_publication == 'vente':
        publication = get_object_or_404(Vendre, id=publication_id)
    elif type_publication == 'location':
        publication = get_object_or_404(Louer, id=publication_id)
    else:
        from django.http import Http404
        raise Http404("Type de publication inconnu.")

    return render(request, 'publication_validee.html', {'publication': publication, 'type_publication': type_publication})

def detail_biens(request, type_bien, pk):
    """
    Vue pour afficher les détails complets d'un bien (vente ou location).
    """
    bien = None
    if type_bien == 'vendre':
        # Tente de récupérer un bien de type Vendre ou renvoie une erreur 404
        bien = get_object_or_404(Vendre, pk=pk)
    elif type_bien == 'louer':
        # Tente de récupérer un bien de type Louer ou renvoie une erreur 404
        bien = get_object_or_404(Louer, pk=pk)
    else:
        # Gérer le cas où le type_bien n'est ni 'vendre' ni 'louer'
        # Vous pouvez rediriger, afficher un message d'erreur, etc.
        # Pour l'instant, on peut simplement lever une 404 ou renvoyer sur la liste des biens
        from django.http import Http404
        raise Http404("Type de bien inconnu.")

    context = {
        'bien': bien,
    }
    return render(request, 'detailsbien.html', context)


def creer_demande_bien(request, type_bien, bien_id):
    bien = None
    if type_bien == 'vendre':
        bien = get_object_or_404(Vendre, pk=bien_id)
    elif type_bien == 'location':
        bien = get_object_or_404(Louer, pk=bien_id)
    else:
        messages.error(request, 'Type de bien invalide.')
        return redirect('some_error_page')

    if request.method == 'POST':
        form = DemandeBienForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Créer la demande
            demande_bien = DemandeBien(
                nom_complet = data['nom_complet'],
                email = data['email'],
                telephone = data['telephone'],
                message = data['message'],
                type_demande = type_bien,
                bien_vente = bien if type_bien == 'vendre' else None,
                bien_location = bien if type_bien == 'location' else None,
            )
            demande_bien.save()

            messages.success(request, 'Votre demande a été envoyée avec succès ! Le propriétaire vous contactera bientôt.')
            return redirect('demande_en_attente')  # Redirige vers la page des biens ou une autre page pertinente
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = DemandeBienForm()

    context = {
        'form': form,
        'bien': bien,
        'type_bien': type_bien,
    }
    return render(request, 'demandebien.html', context)

def is_proprietaire(user):
    # Adaptez cette logique à votre modèle Utilisateur
    # Par exemple, si vous avez un champ 'role' ou si is_staff suffit
    return user.is_authenticated and (user.is_staff or getattr(user, 'role', '') == 'proprietaire')


def liste_demandes_proprietaire(request):  
    demandes = DemandeBien.objects.all().order_by('-date_demande')
    context = {
        'demandes': demandes
    }
    return render(request, 'proprietaire_demande.html', context)

@require_POST
def marquer_demande_traitee(request, pk):
     demande = get_object_or_404(DemandeBien, pk=pk)
     demande.est_traitee = True
     demande.save()
     messages.success(request, "La demande a été marquée comme traitée avec succès !")
     return redirect('liste_demandes_proprietaire')

class DemandeEnAttenteView(TemplateView):
    template_name = 'demande_en_attente.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_principal'] = "Votre demande a bien été envoyée et est en attente de traitement."
        context['message_secondaire'] = "Le propriétaire du bien vous contactera prochainement."
        return context

class DemandeTraiteeSuccesView(TemplateView):
    template_name = 'demande_traitee.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_principal'] = "La demande a été marquée comme traitée avec succès !"
        context['message_secondaire'] = "Les informations ont été mises à jour."
        return context
