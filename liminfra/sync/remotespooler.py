import socket
import json
import traceback
from time import sleep

from liminfra import settings
from liminfra.sync.models import SpoolEntry

if settings.PUSH_DAEMON == False:
	print "%s: Push daemon not enabled" % sys.argv[0]
	sys.exit(1)

destinations = {}
for dmn in settings.SPOOL_DAEMONS:
	if 'spool_remote' in settings.SPOOL_DAEMONS[dmn]:
		destinations[dmn] = settings.SPOOL_DAEMONS[dmn]['spool_remote']
dmns = frozenset(destinations.keys())

sockets = {}
for host in destinations.values():
	sockets[host] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockets[host].connect((host, 6049))

while True:
	spool = SpoolEntry.objects.filter(daemon__in=dmns, state='queued').order_by('id')
	for entry in spool:
		print entry
		n = SpoolEntry.objects.filter(id=entry.id, state='queued').update(state='processing')
		if n != 1:
			print "Ninja'd"
			continue
		entry.state = 'processing'
		try:
			data = json.dumps([entry.daemon, entry.command, entry.arguments])
			sockets[destinations[entry.daemon]].sendall("%03d:%s\n" % (len(data), data))
			ok = sockets[destinations[entry.daemon]].recv(2)
			if ok[0] != '1':
				raise Exception("Remote side refused spoolentry")
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
