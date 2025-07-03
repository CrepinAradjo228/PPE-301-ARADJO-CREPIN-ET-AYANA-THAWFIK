from django.shortcuts import get_object_or_404
from .models import Utilisateur

def proprietaire_id_processor(request):
    """
    Context processor qui ajoute 'proprietaire_id' au contexte
    pour qu'il soit accessible dans tous les templates.
    """

    utilisateur_id = request.session.get('utilisateur_id', None)

    if utilisateur_id is None:
        # Si aucun id utilisateur en session, renvoie None
        return {'proprietaire_id': None}

    try:
        # Récupère l'objet Utilisateur correspondant à l'id en session
        utilisateur_obj = get_object_or_404(Utilisateur, id=utilisateur_id)
        return {'proprietaire_id': utilisateur_obj.id}
    except Utilisateur.DoesNotExist:
        # Si l'utilisateur n'existe pas en base, renvoie None
        return {'proprietaire_id': None}

