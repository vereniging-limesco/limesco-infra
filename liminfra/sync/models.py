import json
from django.db import models
from liminfra import settings

states = (
	('queued', 'Queued'),
	('processing', 'Processing'),
	('processed', 'Processed'),
	('blocked', 'Blocked'),
	('skipped', 'Skipped'),
	('crashed', 'Crashed'),
)
daemon_choices = []
for d, info in settings.SPOOL_DAEMONS.items():
	daemon_choices.append((d, info['name']))

if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
	class EnumField(models.Field):
		def db_type(self, connection):
			return "enum({0})".format(','.join("'%s'" % v[0] for v in self.choices))
else:
	# SQLite snapt enums niet..
	class EnumField(models.CharField):
		def __init__(self, *args, **kwargs):
			if 'max_length' not in kwargs:
				kwargs['max_length'] = max(16, max(map(lambda v: len(v[0]), kwargs['choices'])))
			super(EnumField, self).__init__(*args, **kwargs)

class SpoolEntry(models.Model):
	daemon = EnumField(choices=daemon_choices)
	state = EnumField(choices=states, default='queued')
	command = models.CharField(max_length=32)
	arguments = models.TextField()

	def set_parameters(self, arguments):
		self.arguments = json.dumps(arguments)

	def get_parameter(self, n):
		if self.arguments is None:
			raise ValueError
		return json.loads(self.arguments)[n]

	def get_parameters(self):
		if self.arguments is None:
			return None
		return json.loads(self.arguments)

	def __unicode__(self):
		return "SpoolEntry #%d (%s, %s)" % (self.id, self.daemon, self.command)

	class Meta:
		# indexed_together = ('daemon', 'state')
		db_table = 'sync_spool'
		verbose_name_plural = "spool entries"
