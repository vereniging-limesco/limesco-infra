from django.db import models
from liminfra.portal.models import User

states = (
	('open', 'open'),
	('replied', 'beantwoord'),
	('resolved', 'goedgekeurd'),
	('invalid', 'verworpen'),
	('spam', 'spam'),
)

waitsfor = (
	('', 'nobody'),
	('asker', 'opener'),
	('assignee', 'toegewezen'),
	('support', 'supportdesk'),
)

class EnumField(models.Field):
	def db_type(self, connection):
		return "enum({0})".format(','.join("'%s'" % v[0] for v in self.choices))

class Category(models.Model):
	name = models.CharField(max_length=16, primary_key=True)
	humanName = models.CharField(max_length=32, unique=True)
	restricted = models.BooleanField(default=False, db_index=True)

	def __unicode__(self):
		return self.humanName

class FAQ(models.Model):
	category = models.ForeignKey(Category, db_index=True)
	question = models.CharField(max_length=128)
	answer = models.TextField()

class SupportMember(User):
	level = models.IntegerField(default=1)
	categories = models.ManyToManyField(Category)
	min_level = models.IntegerField(default=1, blank=True, null=True)
	max_level = models.IntegerField(blank=True, null=True)
	signature = models.CharField(max_length=128, blank=True)

class Ticket(models.Model):
	asker = models.ForeignKey(User, db_index=True)
	created = models.DateTimeField(auto_now_add=True)
	level = models.IntegerField(default=1)
	category = models.ForeignKey(Category)
	assignee = models.ForeignKey(SupportMember, blank=True, null=True, db_index=True, related_name='+')
	state = EnumField(choices=states, default='open')
	waitsfor = EnumField(choices=waitsfor, default='')
	private = models.BooleanField()
	subject = models.CharField(max_length=128)

	class Meta:
		# indexed_together = (('category', 'level'), )
		pass

	def add_message(self, user, message, new_waitsfor=None, save=True):
		msg = TicketMessage(ticket=self, person=user, message=message)
		msg.save()
		if not new_waitsfor is None:
			self.waitsfor = new_waitsfor
			if save:
				self.save()

	def take(self, user, chosen=False, save=True):
		tk = TicketTake(ticket=self, person=user, chosen=chosen)
		tk.save()
		self.assignee = user
		if save:
			self.save()

	def abandon(self, user, save=True):
		abndn = TicketAbandon(ticket=self, person=user, old_level=self.level)
		abndn.save()
		self.assignee = None
		if self.state == 'assigned':
			self.state = 'open'
		if user.level <= self.level:
			self.level = user.level + 1
		if save:
			self.save()

	def add_faqreply(self, user, faq, save=True):
		faqr = TicketFAQReply(ticket=self, person=user, faq=faq)
		faqr.save()
		self.state = 'invalid'
		self.waitsfor = ''
		if save:
			self.save()

	def add_bounty(self, user, value):
		bnt = TicketBounty(ticket=self, person=user, value=value)
		bnt.save()

	def file_complaint(self, user, why, save=True):
		cmplnt = TicketComplaint(ticket=self, person=user, against=self.assignee, message=why)
		cmplnt.save()
		self.assignee = None
		self.waitsfor = 'support'
		if save:
			self.save()

	def change_stuff(self, user, new_category=None, new_state=None, new_private=None, new_level=None, new_assignee=-1, new_waitsfor=None, save=True):
		chg = TicketChange(ticket=self, person=user)
		if not new_category is None:
			chg.old_category = self.category
			self.category = new_category
		if not new_state is None:
			chg.old_state = self.state
			self.state = new_state
		if not new_private is None:
			chg.old_private = self.private
			self.private = new_private
		if not new_level is None:
			chg.old_level = self.level
			self.level = new_level
		if new_assignee != -1:
			chg.old_assignee = self.assignee
			self.assignee = new_assignee
		if not new_waitsfor is None:
			self.waitsfor = new_waitsfor
		chg.save()
		if save:
			self.save()

	def mark_invalid(self, user, save=True):
		chg = TicketChange(ticket=self, person=user, old_state=self.state)
		chg.save()
		self.state = 'invalid'
		self.waitsfor = ''
		if save:
			self.save()

	def mark_spam(self, user, save=True):
		chg = TicketChange(ticket=self, person=user, old_state=self.state)
		chg.save()
		self.state = 'spam'
		self.waitsfor = ''
		if save:
			self.save()

	def accept_resolution(self, user, save=True):
		self.state = 'resolved'
		self.waitsfor = ''
		if save:
			self.save()

class TicketHistoryItem:
	def get_type(self):
		return self.__class__.__name__

class TicketMessage(models.Model, TicketHistoryItem):
	ticket = models.ForeignKey(Ticket, db_index=True)
	person = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)
	message = models.TextField()

class TicketChange(models.Model, TicketHistoryItem):
	ticket = models.ForeignKey(Ticket, db_index=True)
	person = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)
	old_category = models.ForeignKey(Category, null=True, blank=True)
	old_state = EnumField(choices=states, null=True, blank=True)
	old_private = models.NullBooleanField()
	old_level = models.IntegerField(null=True, blank=True)
	old_assignee = models.ForeignKey(SupportMember, blank=True, null=True, related_name='+')

class TicketTake(models.Model, TicketHistoryItem):
	ticket = models.ForeignKey(Ticket, db_index=True)
	person = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)
	chosen = models.BooleanField(default=False)

class TicketAbandon(models.Model, TicketHistoryItem):
	ticket = models.ForeignKey(Ticket, db_index=True)
	person = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)
	old_level = models.IntegerField()

class TicketFAQReply(models.Model, TicketHistoryItem):
	ticket = models.ForeignKey(Ticket, db_index=True)
	person = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)
	faq = models.ForeignKey(FAQ)

class TicketBounty(models.Model, TicketHistoryItem):
	ticket = models.ForeignKey(Ticket, db_index=True)
	person = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)
	value = models.DecimalField(max_digits=7, decimal_places=2)

class TicketComplaint(models.Model, TicketHistoryItem):
	ticket = models.ForeignKey(Ticket, db_index=True)
	person = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)
	against = models.ForeignKey(SupportMember, db_index=True, related_name='+')
	message = models.TextField()

