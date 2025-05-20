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
    path('deconnexion/', views.deconnexion_view, name='deconnexion')

]

