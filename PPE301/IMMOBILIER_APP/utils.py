from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('admin_id'):
            messages.error(request, "Veuillez vous connecter pour accéder à cette page.")
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view