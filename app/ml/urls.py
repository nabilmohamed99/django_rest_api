from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from ml import views

router = DefaultRouter()
router.register(r'appariels', views.ApparielViewSet)
router.register(r'AppData',views.AppDataView)
router.register(r'mlmodel',views.MLModelsViewSet,basename='mlmodel')

app_name = 'ml'

urlpatterns = [path('', include(router.urls)),


    path('predict/', views.PredictView.as_view(), name='predict'),
    path('get-data/', views.GetDataView.as_view(), name='get-data'),]

