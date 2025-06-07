from django.contrib import admin
from django.urls import path 
from . import views 

urlpatterns = [
    path('home/', views.home , name="home"),
    path('property/', views.listePublication , name="property"),
    path('landpage/', views.landpage , name="landpage"),
    path('service/', views.service , name="service"),
    path('dashboard/', views.dashboard , name='dashboard'),
    path('contact/', views.contact , name="contact"),
    path('inscription/', views.inscription, name='inscription'),
    path('enregistrerBien/', views.EnregistrerBien, name='enregistrer'),
    path('publierBien/', views.PublierBien, name='publier'),
    path('connexion/', views.connexion_view, name='connexion'),
    path('enregistrerbien/', views.EnregistrerBien, name='registerbien'),
    path('listebien/', views.listeBien, name='listebien'),
    path('publierbien/<int:id>/', views.PublierBien, name='publierbien'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),
    path('ajouter-vente/', views.ajouter_vente, name='ajouter_vente'),
    path('ajouter-location/', views.ajouter_location, name='ajouter_location'),
    path('choixpublication/', views.choix_publication, name='choixpublication'),
    path('valider-publications/', views.valider_publications, name='valider_publication'),
    path('confirmer-validation/<int:id>/', views.confirmer_validation, name='confirmer_validation'),
    path('biens-valides/', views.liste_biens_valides, name='liste_biens_valides'),
    path('dashboard-admin/', views.DashboardAdmin, name='dashboard_admin'),
    path('publication_attente/', views.publication_attente, name='publication_attente'),
    path('publication_validee/', views.publication_validee, name='publication_validee'),
]

