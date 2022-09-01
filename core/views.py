from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from . models import Plane, User
from .  import serializers
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

import uuid


# Create your views here.

class PlaneViewSet(viewsets.ModelViewSet):

    queryset = Plane.objects.all()
    serializer_class = serializers.PlaneSerializer


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            data = request.user
        except:
            return Response('Неверный запрос.', status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.UserSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def subs(self, request):
        if request.user:

            near_sub = User.objects.get_sub_near(request.user)
            middle_sub = User.objects.get_sub_middle(request.user).count()
            far_sub = User.objects.get_sub_far(request.user).count()
            data = {'user': request.user.username,
                    'near_sub': near_sub,
                    'near_sub_count': near_sub.count(),
                    'middle_sub_count': middle_sub,
                    'far_sub_count': far_sub,
                    }
            serializer = serializers.UserSubSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)    
        return Response('Неправильные параметры запроса',status=status.HTTP_400_BAD_REQUEST)

class PaymentView(APIView):

    #permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.PaymentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(request.user)
            return Response('Вы успешно оплатили тариный план', status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
