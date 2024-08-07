from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from ml import views

router = DefaultRouter()
router.register(r'appariels', views.ApparielViewSet)

app_name = 'ml'

urlpatterns = [path('', include(router.urls))]

