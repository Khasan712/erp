from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API's
    path('api/v1/suppliers/', include('api.v1.suppliers.urls')),
    path('api/v1/contracts/', include('api.v1.contracts.urls')),
    path('api/v1/sourcing/', include('api.v1.sourcing.urls')),
    path('api/v1/organization/', include('api.v1.organization.urls')),
    path('api/v1/users/', include('api.v1.users.urls')),
    path('api/v1/items/', include('api.v1.items.urls')),
    path('api/v1/chat/', include('api.v1.chat.urls')),
    path('api/v1/services/', include('api.v1.services.urls')),
    path('api/v1/folders/', include('api.v1.folders.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
