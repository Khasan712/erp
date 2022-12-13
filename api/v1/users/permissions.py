from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import SAFE_METHODS, BasePermission



class IsAdmin(BasePermission):
    message = "You must be the admin of this web site"
    def has_permission(self, request, view):
        if not isinstance(request.user, AnonymousUser):
            # if request.method in SAFE_METHODS:
            return request.user.role == "admin"
        

class IsContractAdministrator(BasePermission):
    message = "You must be the contract administrator of this web site"
    def has_permission(self, request, view):
        if not isinstance(request.user, AnonymousUser):
            # if request.method in SAFE_METHODS:
            return request.user.role == "contract_administrator"
        

class IsCategoryManager(BasePermission):
    message = "You must be the category manager of this web site"
    def has_permission(self, request, view):
        if not isinstance(request.user, AnonymousUser):
            # if request.method in SAFE_METHODS:
            return request.user.role == "category_manager"

class IsLawyer(BasePermission):
    message = "You must be the lawyer of this web site"

    def has_permission(self, request, view):
        if not isinstance(request.user, AnonymousUser):
            # if request.method in SAFE_METHODS:
            return request.user.role == "lawyer"
        

class IsSourcingAdministrator(BasePermission):
    message = "You must be the sourcing administrator of this web site"

    def has_permission(self, request, view):
        if not isinstance(request.user, AnonymousUser):
            # if request.method in SAFE_METHODS:
            return request.user.role == "sourcing_administrator"


class IsSupplier(BasePermission):
    message = "You must be the supplier of this web site"

    def has_permission(self, request, view):
        if not isinstance(request.user, AnonymousUser):
            # if request.method in SAFE_METHODS:
            return request.user.role == "supplier"


class IsSourcingDirector(BasePermission):
    """
        Organization director
    """
    message = "You must be the sourcing director of this web site"

    def has_permission(self, request, view):
        if not isinstance(request.user, AnonymousUser):
            # if request.method in SAFE_METHODS:
            return request.user.role == "sourcing_director"


# class IsBuyer(BasePermission):
#     message = "You must be the buyer of this web site"

#     def has_permission(self, request, view):
#         if not isinstance(request.user, AnonymousUser):
#             # if request.method in SAFE_METHODS:
#             return request.user.role == "buyer"
        
        
# class IsStorekeeper(BasePermission):
#     message = "You must be the storekeeper of this web site"

#     def has_permission(self, request, view):
#         if not isinstance(request.user, AnonymousUser):
#             # if request.method in SAFE_METHODS:
#             return request.user.role == "storekeeper"
            
        
        
