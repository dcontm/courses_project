#from typing_extensions import Required
from rest_framework import serializers
from django.core import signing
from . import models
from . mail_gun import send_email_from_mailgun

class PlaneSerializer(serializers.ModelSerializer):

	class Meta:

		model = models.Plane
		fields = '__all__'

class UserInvSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.User
		fields = ['id', 'username', 'avatar']

class UserSerializer(serializers.ModelSerializer):

	date_joined = serializers.ReadOnlyField()
	plane = PlaneSerializer()
	inv_near = UserInvSerializer()

	# Необязательное поле username приглашающего
	invite_from = serializers.CharField(required=False)


	class Meta:

		model = models.User
		fields = '__all__'
		extra_kwargs = {'password': {'write_only': True}}
		
	def create(self, validated_data):

        # Пытаемся получить поле, если поле не заполнено получаем None
		inviter = validated_data.get('invite_from')
		
		if inviter:
			# Если поле заполнено пытаемся получить обьект, если не удаеться поднимаем исключение
			try:
				inviter = models.User.objects.get(username=inviter)
			except:
				raise serializers.ValidationError('Пользователя, пригласившего вас, не существует. Пожайлуста проверьте введенные данные.')
				
		user = models.User(username=validated_data['username'],
                email=validated_data['email'],
                is_active=False)
		user.set_password(validated_data['password'])
		user.save()
        # Устанавливаем цепочку инвайтеров, если поле не заполнено устанавливается None
		user.set_chain_inviters(inviter)

        # Формируем хеш для верификации емайл
		postfix = signing.dumps({'user_id': user.id}, salt='veryfication_email_salt')
		verify_url = f'http://127.0.0.1:8000/auth0/verify-email/{postfix}/'
        #send_email_from_mailgun('Hello from DREAM TEAM', 
                                #verify_url,
                                #_to = user.email)
		return user


class UserSubSerializer(serializers.Serializer):

	user = serializers.CharField()
	near_sub = UserSerializer(many=True)
	near_sub_count = serializers.IntegerField()
	middle_sub_count = serializers.IntegerField()
	far_sub_count = serializers.IntegerField()

class PaymentSerializer(serializers.Serializer):

	plane_id = serializers.IntegerField(required=True)

	def save(self, user):
		plane_id = self.validated_data['plane_id']
		try:
			plane = models.Plane.objects.get(pk=plane_id)
		except:
			raise serializers.ValidationError('Данный тарифный план больше недоступен.')
		print('Платеж успешно подтвержден')
		user.payment_event(plane)
		
