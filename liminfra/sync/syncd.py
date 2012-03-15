import sys
import os
import traceback
from time import sleep

from liminfra import settings
from liminfra.sync.models import SpoolEntry
from django.db import transaction

class CommandList:
	def __init__(self):
		self.ht = dict()

	def register(self, method):
		self.ht[method.func_name] = method

	def unregister(self, method):
		del self.ht[method.func_name]

	def get(self, name):
		return self.ht[name]

def run(dmn, commands):
	print dmn
	while True:
		# Workaround voor bug waarin hij de nieuwe entries niet kan vinden
		# [2012-03-15 quis] Bug-solver krijgt een biertje
		transaction.commit_unless_managed()

		spool = SpoolEntry.objects.filter(daemon=dmn['name'], state='queued').order_by('id')
		for entry in spool:
			print entry
			n = SpoolEntry.objects.filter(id=entry.id, state='queued').update(state='processing')
			if n != 1:
				print "Ninja'd"
				continue
			entry.state = 'processing'
			try:
				fnc = commands.get(entry.command)
				fnc(entry)
			except:
				traceback.print_exc()
				entry.state = 'crashed'
			else:
				entry.state = 'processed'
			entry.save()
		try:
			sleep(1)
		except KeyboardInterrupt:
			break

def skip_queued_items(dmn, cmd, arguments=None):
	qs = SpoolEntry.objects.filter(daemon=dmn, state='queued')
	if arguments is not None:
		qs = qs.filter(arguments=arguments)
	qs.update(state='skipped')

if __name__ == '__main__':
	name = sys.argv[1]
	dmn = settings.SPOOL_DAEMONS[name]

	commands = CommandList()
	mod = __import__(name, level=1)
	mod.init(commands)

	if os.getuid() != dmn['uid']:
		print "%s: Uid should be %d instead of %d" % (sys.argv[0], dmn['uid'], os.getuid())
		sys.exit(1)

	if os.getgid() != dmn['gid']:
		print "%s: Gid should be %d instead of %d" % (sys.argv[0], dmn['gid'], os.getgid())
		sys.exit(1)

	run(dmn, commands)
