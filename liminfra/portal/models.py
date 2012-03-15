from django.db import models
import django.contrib.auth.models as auth_models

class User(auth_models.User):
	public_name = models.CharField(max_length=60)
	is_male = models.BooleanField(default=True) # helaas ;)

	def __unicode__(self):
		return self.public_name

class Group(auth_models.Group):
	humanName = models.CharField(max_length=80, unique=True)
	genitive_prefix = models.CharField(max_length=20, default='van de')

class Seat(models.Model):
	name = models.CharField(max_length=80)
	humanName = models.CharField(max_length=120)
	description = models.TextField()
	group = models.ForeignKey(Group)
	member = models.ForeignKey(User)
