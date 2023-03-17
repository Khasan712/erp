from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from drf_yasg import openapi as drf_yasg_openapi
from drf_yasg import views as drf_yasg_views
from rest_framework import permissions
from rest_framework.schemas import get_schema_view

schema_view = drf_yasg_views.get_schema_view(
    drf_yasg_openapi.Info(
        title="Erp API",
        default_version="v1",
        description="Erp API",
        contact=drf_yasg_openapi.Contact(email="info.kamalov@gmail.com"),
        license=drf_yasg_openapi.License(name="Proprietary software license"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API's
    path('api/v1/suppliers/', include('api.v1.suppliers.urls')),
    path('api/v1/contracts/', include('api.v1.contracts.urls')),
    path('api/v1/sourcing/', include('api.v1.sourcing.urls')),
    path('api/v1/organization/', include('api.v1.organization.urls')),
    path('api/v1/users/', include('api.v1.users.urls')),
    path('api/v1/items/', include('api.v1.items.urls')),
    # path('api/v1/chat/', include('api.v1.chat.urls')),
    path('api/v1/services/', include('api.v1.services.urls')),
    path('api/v1/folders/', include('api.v1.folders.urls')),

    # Swagger
    path("schema/", get_schema_view(title="API's", description="API for Erp contract",), name="openapi-schema",),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui",),
    path("swagger/json/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/yaml/", schema_view.without_ui(cache_timeout=0), name="schema-yaml"),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
