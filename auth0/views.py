from rest_framework.views import APIView
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from . serializers import PasswordResetSerializer, PasswordResetVerifySerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

from django.core import signing
from core.serializers import UserSerializer
from django.conf import settings


from django.contrib.auth.password_validation import validate_password


USER = get_user_model()
MAX_AGE = 60*60*48 # Время жизни сигнатуры signing


class SingupView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, verify_key):
        try:
            print(verify_key)
            user_id = signing.loads(verify_key, salt='veryfication_email_salt', max_age=MAX_AGE).get('user_id')
            user = USER.objects.get(pk=user_id)
            user.is_active = True
            user.save()
            return Response('Вы успешно завершили регистрацию.', status=status.HTTP_200_OK)

        except signing.SignatureExpired:
            message = 'Срок жизни данной ссылки истек. Повторите процедуру регистрации.'
            return Response({'message':message}, status=status.HTTP_400_BAD_REQUEST)
        except signing.BadSignature:
            message =  'Проверочный токен поврежден. Повторите попытку или обратитесь в службу поддержки.'
        return Response({'message':message}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user = USER.objects.get(email=request.data.get('email'))
                prefix = signing.dumps({'user_id': user.id}, salt='reset_password_salt')
                reset_url = 'http://127.0.0.1:8000/auth0/password/reset/verify/' + prefix + '/'
                print(reset_url)
                return Response('На указанную вами почту выслано письмо со ссылкой для сброса пароля.', status=status.HTTP_200_OK)
            except:
                message= 'Произошла не предвиденная ошибка.Повторите попытку или обратитесь в службу поддержки.'
                return Response({'message':message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ResetPasswordVerifyView(APIView):

    permission_classes = [AllowAny]

    def get_user(self, verify_key):
        user_id = signing.loads(verify_key,salt='reset_password_salt', max_age=MAX_AGE).get('user_id')
        user = USER.objects.get(pk=user_id)
        return user

    def post(self, request, verify_key):
        serializer = PasswordResetVerifySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                user = self.get_user(verify_key)
                password = validate_password(request.data['password'])
                password = request.data['password']
                user.set_password(password)
                user.save()
                return Response('Пароль успешно обновлен', status=status.HTTP_200_OK)
        
            except signing.SignatureExpired:
                message = 'Срок жизни данной ссылки истек. Повторите процедуру регистрации.'
                return Response({'message':message}, status=status.HTTP_400_BAD_REQUEST)
            except signing.BadSignature:
                message =  'Проверочный токен поврежден. Повторите попытку или обратитесь в службу поддержки.'
            except :
                message = 'Неизвестная ошибка.'
            return Response({'message':message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
