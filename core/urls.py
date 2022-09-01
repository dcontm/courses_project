from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'planes', views.PlaneViewSet)
router.register(r'users', views.UserViewSet)


urlpatterns = [
	path('', include(router.urls)),
	path('payments/', views.PaymentView.as_view(), name='payments' )
]
