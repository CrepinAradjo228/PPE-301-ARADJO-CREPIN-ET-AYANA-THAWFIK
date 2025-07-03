from django.contrib import admin
from django.urls import path 
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('home/', views.home , name="home"),
    path('property/', views.listePublication , name="property"),
    path('landpage/', views.landpage , name="landpage"),
    path('service/', views.service , name="service"),
    path('dashboard/', views.dashboard , name='dashboard'),
    path('contact/', views.contact , name="contact"),
    path('inscription/', views.inscription, name='inscription'),
    path('enregistrerBien/', views.EnregistrerBien, name='enregistrer'),
    path('publierBien/<int:id>/', views.PublierBien, name='publier'),
    path('connexion/', views.connexion_view, name='connexion'),
    path('enregistrerbien/', views.EnregistrerBien, name='registerbien'),
    path('listebien/<int:proprietaire_id>/', views.listeBien, name='listebien'),
    path('bienpublies/', views.bienpublies, name='bienpublies'),
    path('publierbien/<int:id>/', views.PublierBien, name='publierbien'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),
    path('ajouter-vente/', views.ajouter_vente, name='ajouter_vente'),
    path('ajouter-location/', views.ajouter_location, name='ajouter_location'),
    path('choixpublication/<int:id>/', views.choix_publication, name='choixpublication'),
    path('valider-publications/', views.valider_publications, name='valider_publication'),
    path('confirmer-validation/<str:type_publication>/<int:publication_id>/', views.confirmer_validation, name='confirmer_validation'),
    path('biens-valides/', views.liste_biens_valides, name='liste_biens_valides'),
    path('dashboard-admin/', views.DashboardAdmin, name='dashboard_admin'),
    path('publication_attente/<str:type_publication>/<int:publication_id>/', views.publication_attente, name='publication_attente'),
    path('publication_validee/<str:type_publication>/<int:publication_id>/', views.publication_valides, name='publication_validee'),
    path('properties/<str:type_bien>/<int:pk>/', views.detail_biens, name='details_bien_client'),
    path('demandebien/creer/<str:type_bien>/<int:bien_id>/', views.creer_demande_bien, name='creer_demande_bien'),
    path('proprietaire/demandes/', views.liste_demandes_proprietaire, name='liste_demandes_proprietaire'),
    path('demande/<int:pk>/traiter/', views.marquer_demande_traitee, name='marquer_demande_traitee'),
    path('demande/en-attente/', views.demande_en_attente, name='demande_en_attente'),
    path('demande/traitee/succes/', views.demande_traitee_succes, name='demande_traitee_succes')
]   

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

