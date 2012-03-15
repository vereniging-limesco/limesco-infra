import socket
import json
import sys
import traceback
from cStringIO import StringIO

from liminfra import settings
from liminfra.sync.models import SpoolEntry

# TODO connecties asynchroon afhandelen
# TODO Betere inputchecking
# TODO securitychecks op wie welke data mag spoolen

if settings.LISTEN_DAEMON == False:
	print "%s: Set LISTEN_DAEMON to the address to bind on" % sys.argv[0]
	sys.exit(1)

ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ss.bind((settings.LISTEN_DAEMON, 6049))
ss.listen(5)

while True:
	s, addr = ss.accept()
	while True:
		try:
			buf = s.recv(4)
			if not buf:
				break
			buf = s.recv(int(buf[0:3]) + 1)[:-1]
			data = json.loads(buf)
			try:
				se = SpoolEntry(daemon=data[0], command=data[1])
				if len(data) == 3:
					se.arguments = data[2]
				se.save()
			except:
				traceback.print_exc()
				s.sendall("0\n")
				continue
			s.sendall("1\n")
		except:
			traceback.print_exc()
			break
	s.close()
