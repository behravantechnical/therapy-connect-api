from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Admin URLs
admin_urlpatterns = [
    path("admin/", admin.site.urls),
]

# Accounts App URLs
accounts_urlpatterns = [
    path(
        "api/accounts/", include("therapy_connect.accounts.urls", namespace="accounts")
    ),
]

# Profiles App URLs
profiles_urlpatterns = [
    path(
        "api/profiles/v1/",
        include("therapy_connect.profiles.urls", namespace="profiles"),
    ),
]

# therapy App URLs
therapy_urlpatterns = [
    path(
        "api/therapy/v1/",
        include("therapy_connect.therapy.urls", namespace="therapy"),
    ),
]

# Schema URLs
schema_urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]

# Combine all URL patterns
urlpatterns = (
    admin_urlpatterns
    + accounts_urlpatterns
    + profiles_urlpatterns
    + therapy_urlpatterns
    + schema_urlpatterns
)


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
