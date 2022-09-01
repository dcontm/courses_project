from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import pre_save, post_save, post_delete
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from . utils import validate_avatar, path_avatar
# Create your models here.

class Plane(models.Model):

	''' Модель тариф - параметры тарифов '''
	title = models.CharField(max_length=50)
	description = models.CharField(max_length=500)
	period = models.PositiveSmallIntegerField(default=0)
	price = models.PositiveIntegerField(default=0)
	first_bonus = models.DecimalField( max_digits=3, decimal_places=2)
	near_bonus = models.DecimalField( max_digits=3, decimal_places=2)
	middle_bonus = models.DecimalField( max_digits=3, decimal_places=2)
	far_bonus = models.DecimalField( max_digits=3, decimal_places=2)

	def __str__(self):
		return f'{self.title}'


class Event(models.Model):

	BALANCE = 'B'
	FOLLOWER = 'F'
	SUBSCRIBE = 'S'


	TYPE = (
		(BALANCE, 'balanse'),
		(FOLLOWER, 'follower'),
		(SUBSCRIBE, 'subscribe')
	)

	class Actions(models.IntegerChoices):

		# Действия с балансом
		payoff = 1 # вывод средств
		reward_new = 100 # начисление вознаграждения за нового фолловера 1 уровня
		reward_near = 101 # начисление вознаграждения за фолловера 1 уровня
		reward_middle = 102 # начисление вознаграждения за фолловера 2 уровня
		reward_far = 103 # начисление вознаграждения за фолловера 3 уровня

		# Действия фолловеров 
		new_follower_registed = 201 # Новый фолловер зарегистирован
		new_follower_prolong = 202 # Новый фолловер офрмил подписку (1 лвл)
		follower_prolong = 203 #  Фолловер продлил подписку (1 лвл)

		# Подписка
		end_period = 301 # Период подписки завершен
		start_period = 302 # Новый период подписки оформлен
		paymount = 303 # Оплата подписки

	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='transaction', on_delete=models.CASCADE)
	action = models.IntegerField(choices=Actions.choices)
	dt = models.DateTimeField(default=timezone.now)
	type = models.CharField(max_length=1, choices= TYPE)
	amount = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)


	def save(self, *args, **kwargs):
		try:
			return super(Event, self).save(*args,**kwargs)
		except:
			pass

	def __str__(self):
		return self.user.username


class UserManager(UserManager):

	# Вернуть подписчиков, которых непосредсвенно пригласил пользователь.
	# Первая ступень.
	def get_sub_near(self, user):
		subs = super().get_queryset().filter(inv_near = user)
		return subs

	# Вернуть подписчиков, подписанных на подписчиков пользователя.
	# Вторая ступень.
	def get_sub_middle(self, user):
		subs = super().get_queryset().filter(inv_middle = user)
		return subs
	
	# Вернуть подписчиков, подписанных на подписчиков подписчиков пользователя.
	# Третья ступень.
	def get_sub_far(self, user):
		subs = super().get_queryset().filter(inv_far = user)
		return subs

	# Проверка                
	def check_end_period(self):
		users = super().get_queryset().filter(is_open=True)
		for user in users:
			pass



class User(AbstractUser):
	avatar = ProcessedImageField(upload_to = path_avatar,default='avatars/default-XRANGE202418022019.jpg', 
								    processors=[ResizeToFill(100, 100)], 
								    format='JPEG', options={'quality': 50} ,
								    validators=[validate_avatar],
								    blank=True, 
								    null=True,
									)
	email = models.EmailField(max_length=100, unique=True)
	balanse = models.PositiveIntegerField(default=0)
	code = models.CharField(max_length=6, unique=True, blank=True, null=True)
	plane = models.ForeignKey('Plane', on_delete=models.SET_NULL, blank=True, null=True)
	is_open = models.BooleanField(default=False)
	is_blocked = models.BooleanField(default=False)
	start = models.DateTimeField(blank=True, null= True)
	end = models.DateTimeField(blank=True, null= True)

	is_new = models.BooleanField(default=True)

	inv_near = models.ForeignKey('self', related_name='rel_inv_near', on_delete=models.SET_NULL, blank=True, null=True)
	inv_middle = models.ForeignKey('self', related_name='rel_inv_middle', on_delete=models.SET_NULL, blank=True, null=True)
	inv_far = models.ForeignKey('self', related_name='rel_inv_far', on_delete=models.SET_NULL, blank=True, null=True)

	objects = UserManager()

	REQUIRED_FIELDS = ['email']

	def __str__(self):
		return self.username

	def has_add_bonus(self):
		''' Проверка возможно ли зачисление бонусов '''
		if self.is_open and not self.is_blocked:
			return True
		else:
			return False
	
	def set_chain_inviters(self, invite_from):
		self.inv_near = invite_from
		if self.inv_near:
			self.inv_middle = invite_from.inv_near
		if self.inv_middle:
			self.inv_far = invite_from.inv_middle
		self.save()


	def add_bonus_inviters(self, plane):
		if self.inv_near and self.inv_near.has_add_bonus():
			if self.is_new:
				bonus = self.plane.price * self.inv_near.plane.first_bonus
				self.inv_near.balanse += bonus
				self.inv_near.save()
				self.is_new = False
				self.save()
				Event.objects.create(user=self.inv_near, type='B', action=100, amount=bonus)
			elif self.is_new == False:
				bonus = self.plane.price * self.inv_near.plane.near_bonus
				self.inv_near.balanse += bonus
				self.inv_near.save()
				Event.objects.create(user=self.inv_near, type='B', action=101, amount=bonus)

		if self.inv_middle and self.inv_middle.has_add_bonus():
			bonus = self.plane.price * self.inv_middle.plane.middle_bonus
			self.inv_middle.balanse += bonus
			self.inv_middle.save()
			Event.objects.create(user=self.inv_middle, type='B', action=102, amount=bonus)

		if self.inv_far and self.inv_far.has_add_bonus():
			bonus = self.plane.price * self.inv_far.plane.far_bonus
			self.inv_far.balanse += bonus
			self.inv_far.save()
			Event.objects.create(user=self.inv_far, type='B', action=103, amount=bonus)


	def payment_event(self, plane):
		#Событие пролдения или активации подписки
		self.plane = plane
		self.is_open = True

		if self.end and (self.end > timezone.now()):
			# Продление действующей подписки
			self.end += timezone.timedelta(days=plane.period)
			event_follower = Event(user=self.inv_near, type='F', action = 203)

		elif not self.end:
			# Новый пользователь активировал подписку
			self.end = timezone.now() + timezone.timedelta(days=plane.period)
			event_follower = Event(user=self.inv_near, type='F', action = 202)

		else:
			# Активация нового периода подписки
			self.end = timezone.now() + timezone.timedelta(days=plane.period)
			event_follower = Event(user=self.inv_near, type='F', action = 203)

		
		self.save()

		#Уведомления
		Event.objects.create(user=self, type='S', action=303, amount=plane.price) # Оплата
		Event.objects.create(user=self, type='S', action=302)  # Изменение срока действие подписки
		event_follower.save() # Событие активации/продления подписки фолловером 1(лвл)

		# Начисление бонусов инвайтерам
		self.add_bonus_inviters(plane)

	
		




