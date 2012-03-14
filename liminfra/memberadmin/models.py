from django.db import models

class Member(models.Model):
	username = models.CharField(max_length=30, unique=True, help_text="Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters")
	email = models.EmailField(blank=True)
	password = models.CharField(max_length=128, help_text="Use '[algo]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>.")
	groups = models.ManyToManyField('Group', verbose_name='groups', blank=True)
	is_active = models.BooleanField(default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.")

	first_name = models.CharField(max_length=30, blank=True)
	last_name = models.CharField(max_length=30, blank=True)
	birthdate = models.DateField(null=True, blank=True)
	is_male = models.BooleanField(default=True) # helaas ;)
	public_name = models.CharField(max_length=60)

	telephone = models.CharField(max_length=20, blank=True)
	addr_street = models.CharField(max_length=100, blank=True)
	addr_number = models.CharField(max_length=20, blank=True)
	addr_zip = models.CharField(max_length=10, blank=True)
	addr_city = models.CharField(max_length=80, blank=True)

	def get_full_name(self):
		bits = self.last_name.split(',', 1)
		if len(bits) == 1:
			return self.first_name + ' ' + self.last_name
		return self.first_name + bits[1] + ' ' + bits[0]

	def __unicode__(self):
		return self.get_full_name()

class Group(models.Model):
	name = models.CharField(max_length=80, unique=True)
	humanName = models.CharField(max_length=80, unique=True)
	genitive_prefix = models.CharField(max_length=20, default='van de')

	def __unicode__(self):
		return self.name

class Seat(models.Model):
	name = models.CharField(max_length=80)
	humanName = models.CharField(max_length=120)
	description = models.TextField()
	group = models.ForeignKey(Group)
	member = models.ForeignKey(Member)
