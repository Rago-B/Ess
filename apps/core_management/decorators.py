
from django.core.exceptions import PermissionDenied
from functools import wraps

def allowed_roles(allowed_list=[]):
    """
    Unified RBAC structural interceptor.
    Checks the user's custom role field property string natively before view execution.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Fetch custom database column string parameter value safely
            user_role = getattr(request.user, 'role', 'employee')
            
            # 2. Grant dynamic master pass bypass constraints for superuser profiles
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            # 3. Access checking verification matching your roles list array
            if user_role in allowed_list:
                return view_func(request, *args, **kwargs)
            else:
                # Triggers standard Django 403 authorization lock error page frame natively
                raise PermissionDenied("Access Denied: Your security clearance tier is insufficient.")
                
        return _wrapped_view
    return decorator
