from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from api import urls as api_urls
from core import urls as core_urls
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from api import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Документация Django API",
        default_version="v1",
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.IsAdminUser]
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include(core_urls)),
    path('api/', include(api_urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('doc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path("__debug__/", include("debug_toolbar.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
