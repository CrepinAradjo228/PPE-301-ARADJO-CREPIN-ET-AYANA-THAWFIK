from django.shortcuts import get_object_or_404
from .models import Utilisateur

def proprietaire_processor(request):
    """
    Context processor qui ajoute l'objet utilisateur et son ID au contexte
    pour les rendre accessibles dans tous les templates.
    """
    utilisateur_id = request.session.get('utilisateur_id', None)

    if utilisateur_id is None:
        return {'proprietaire': None, 'proprietaire_id': None}

    try:
        # Récupère l'objet Utilisateur correspondant à l'id en session
        utilisateur_obj = get_object_or_404(Utilisateur, id=utilisateur_id)
        
        # Renvoie un dictionnaire avec l'objet utilisateur et son ID
        return {
            'proprietaire': utilisateur_obj,
            'proprietaire_id': utilisateur_obj.id
        }
    except Utilisateur.DoesNotExist:
        # Si l'utilisateur n'existe pas en base, renvoie None
        return {'proprietaire': None, 'proprietaire_id': None}
