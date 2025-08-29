from django.contrib import admin
from django.urls import path 
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('home/', views.home , name="home"),
    path('property/', views.listePublication , name="property"),
    path('landpage/', views.landpage , name="landpage"),
    path('homepage/', views.homepage , name="service"),
    path('dashboard/', views.dashboard , name='dashboard'),
    path('contact/', views.contact , name="contact"),
    path('inscription/', views.inscription, name='inscription'),
    path('enregistrerBien/', views.EnregistrerBien, name='enregistrer'),
    path('supprimer_bien/<int:bien_id>/', views.supprimer_bien, name='supprimer_bien'),
    path('modifier_bien/<int:bien_id>/', views.modifier_bien, name='modifier_bien'),
    path('publierBien/<int:id>/', views.PublierBien, name='publier'),
    path('connexion/', views.connexion_view, name='connexion'),
    path('enregistrerbien/', views.EnregistrerBien, name='registerbien'),
    path('listebien/<int:proprietaire_id>/', views.listeBien, name='listebien'),
    path('bienpublies/', views.bienpublies, name='bienpublies'),
    path('publierbien/<int:id>/', views.PublierBien, name='publierbien'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),
    path('ajouter-vente/', views.ajouter_vente, name='ajouter_vente'),
    path('republier-vente/<int:publication_id>/', views.republier_vente, name='republier_vente'),
    path('ajouter-location/', views.ajouter_location, name='ajouter_location'),
    path('republier-location/<int:publication_id>/', views.republier_location, name='republier_location'),
    path('modifier_vente/<int:vente_id>/', views.modifier_vente, name='modifier_vente'),
    path('supprimer_vente/<int:vente_id>/', views.supprimer_vente, name='supprimer_vente'),
    path('modifier_location/<int:location_id>/', views.modifier_location, name='modifier_location'),
    path('supprimer_location/<int:location_id>/', views.supprimer_location, name='supprimer_location'),
    path('choixpublication/<int:id>/', views.choix_publication, name='choixpublication'),
    path('valider-publications/', views.valider_publications, name='valider_publication'),
    path('confirmer-validation/<str:type_publication>/<int:publication_id>/', views.confirmer_validation, name='confirmer_validation'),
    path('biens-valides/', views.liste_biens_valides, name='liste_biens_valides'),
    path('dashboard-admin/', views.DashboardAdmin, name='dashboard_admin'),
    path('publication_attente/<str:type_publication>/<int:publication_id>/', views.publication_attente, name='publication_attente'),
    path('publication_validee/<str:type_publication>/<int:publication_id>/', views.publication_valides, name='publication_validee'),
    path('publication_refusee/<str:type_publication>/<int:publication_id>/', views.publication_refusee, name='publication_refusee'),
    path('properties/<str:type_bien>/<int:pk>/', views.detail_biens, name='details_bien_client'),
    path('demandebien/creer/<str:type_bien>/<int:bien_id>/', views.creer_demande_bien, name='creer_demande_bien'),
    path('proprietaire/demandes/', views.liste_demandes_proprietaire, name='liste_demandes_proprietaire'),
    path('Proprietaires/demandes/traiter/<int:pk>/', views.marquer_demande_traitee, name='marquer_demande_traitee'),
    path('admin/transactions/', views.liste_transactions, name='liste_transactions'), # Nouvelle URL pour les transactions
    path('demande/en-attente/', views.demande_en_attente, name='demande_en_attente'),
    path('error/', views.page_erreur, name='some_error_page'),
    path('location/renouveler/<int:bien_id>/', views.renouveler_location, name='renouveler_location'),
     path('soumettre-documents-vente/<int:demande_pk>/', views.soumettre_documents_vente, name='soumettre_documents_vente'),
    path('documents-a-valider/', views.liste_documents_a_valider, name='liste_documents_a_valider'),
    path('valider-document/<int:pk>/', views.valider_document, name='valider_document'),
    path('documents-valides/', views.liste_documents_valides, name='liste_documents_valides'), # Nouvelle URL
    path('admin/login/', views.admin_login, name='admin_login'),
    path('demande/<int:demande_id>/confirmer_suppression/', views.confirmer_suppression_demande, name='confirmer_suppression_demande'),
    path('demande/<int:demande_id>/supprimer/', views.supprimer_demande_bien, name='supprimer_demande_bien'),
    path('admin/refuser-publication/<str:bien_type>/<int:bien_id>/', views.refuser_publication, name='refuser_publication'),
    path('biens-refuses/', views.biens_refuses, name='biens_refuses'),
    path('demande/traitee/succes/', views.demande_traitee_succes, name='demande_traitee_succes')
]   

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

