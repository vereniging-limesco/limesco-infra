from django.db import models
from django.contrib.auth.models import User, Group

class Member(User):
	birthdate = models.DateField(null=True, blank=True)
	is_male = models.BooleanField(default=True) # helaas ;)

	telephone = models.CharField(max_length=20, null=True)
	addr_street = models.CharField(max_length=100, blank=True)
	addr_number = models.CharField(max_length=20, blank=True)
	addr_zip = models.CharField(max_length=10, blank=True)
	addr_city = models.CharField(max_length=80, blank=True)

	def get_full_name(self):
		bits = self.last_name.split(',', 1)
		if len(bits) == 1:
			return self.first_name + ' ' + self.last_name
		return self.first_name + bits[1] + ' ' + bits[0]

class Seat(models.Model):
	name = models.CharField(max_length=80)
	humanName = models.CharField(max_length=120)
	description = models.TextField()
	group = models.ForeignKey(Group)
	member = models.ForeignKey('Member')
