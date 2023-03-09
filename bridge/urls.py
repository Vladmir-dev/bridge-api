from drf_yasg import openapi
from django.urls import include
from django.urls import re_path as url
from rest_framework import routers
from .views import AuthViewSet,PostCreateView
from django.conf import settings
from django.views.generic import TemplateView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from django.conf import settings
from django.conf.urls.static import static


schema_view = get_schema_view(
   openapi.Info(
      title="Bridge API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

if settings.DEBUG:
    router = routers.DefaultRouter()
else:
    router = routers.SimpleRouter()


router.register(r"auth", AuthViewSet, basename="auth")
# router.register(r'auth/posts', PostCreateView)

urlpatterns = [
    url(r'^api/v1/', include(router.urls)),
    url(r'^$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^api/v1/auth/create-post', PostCreateView.as_view(), name="post_create")
]

urlpatterns += static(settings.STATIC_URL)
urlpatterns += static(settings.MEDIA_URL)