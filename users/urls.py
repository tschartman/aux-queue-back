from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users import views

router = DefaultRouter()
router.register(r'users', views.UserViewset, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]