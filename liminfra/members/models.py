from django.db import models
import django.contrib.auth.models as auth_models
from django.db.models.signals import m2m_changed
from django.core.mail import EmailMessage

from liminfra.sync.util import add_spool_entry

class User(auth_models.User):
	birthdate = models.DateField(null=True, blank=True)
	is_male = models.BooleanField(default=True) # helaas ;)
	paid_2012 = models.BooleanField()
	public_name = models.CharField(max_length=60)

	telephone = models.CharField(max_length=20, blank=True)
	addr_street = models.CharField(max_length=100, blank=True)
	addr_number = models.CharField(max_length=20, blank=True)
	addr_zip = models.CharField(max_length=10, blank=True)
	addr_city = models.CharField(max_length=80, blank=True)

	remarks = models.TextField(blank=True)

	def get_full_name(self):
		bits = self.last_name.split(',', 1)
		if len(bits) == 1:
			return self.first_name + ' ' + self.last_name
		return self.first_name + bits[1] + ' ' + bits[0]

	def __unicode__(self):
		return self.get_full_name()

	def save(self, *args, **kwargs):
		hadId = self.id
		super(User, self).save(*args, **kwargs)
		add_spool_entry('postfix', 'update_domain_map', 'leden.limesco.nl')
		# XXX support voor e-mailadres wijzigen
		cmd = 'add_list_members' if not hadId else 'update_list_member_settings'
		add_spool_entry('mailman', cmd, ['announce', 'lists.limesco.nl', [self.email]])
		if not hadId:
			add_spool_entry('wiki', 'create_user', [self.username, self.password])
			em = """Dag %(public_name)s,

Welkom bij Limesco! Een fatsoenlijke introductiemail volgt nog.

Met een vriendelijke groet,
Het Limesco secretariaat
""" % {'username': self.username, 'public_name': self.public_name}
			email = EmailMessage("Welkom bij Limesco!", em, 'Limesco secretariaat <secretariaat@limesco.nl>', [self.email])
			email.send()

	def delete(self, *args, **kwargs):
		super(User, self).delete(*args, **kwargs)
		add_spool_entry('mailman', 'remove_list_members', ['announce', 'lists.limesco.nl', [self.email]])

class Group(auth_models.Group):
	humanName = models.CharField(max_length=80, unique=True)
	genitive_prefix = models.CharField(max_length=20, default='van de')

	def __unicode__(self):
		return self.name

	def save(self, *args, **kwargs):
		hadId = self.id
		super(Group, self).save(*args, **kwargs)
		if not hadId:
			add_spool_entry('mailman', 'create_list', [self.name, 'lists.limesco.nl'])

class Seat(models.Model):
	name = models.CharField(max_length=80)
	humanName = models.CharField(max_length=120)
	description = models.TextField()
	group = models.ForeignKey(Group)
	user = models.ForeignKey(User)

def m2m_change(sender, **kwargs):
	if kwargs['action'] == 'post_add':
		cmd = 'add_list_members'
	elif kwargs['action'] == 'post_remove':
		cmd = 'remove_list_members'
	# XXX post_clear..
	else:
		return
	if not kwargs['reverse']:
		groups = Group.objects.filter(id__in=kwargs['pk_set'])
		for grp in groups:
			add_spool_entry('mailman', cmd, [grp.name, 'lists.limesco.nl', [kwargs['instance'].email]])
	else:
		users = User.objects.filter(id__in=kwargs['pk_set'])
		add_spool_entry('mailman', cmd, [kwargs['instance'].name, 'lists.limesco.nl', [user.email for user in users]])

m2m_changed.connect(m2m_change, sender=User.groups.through)
