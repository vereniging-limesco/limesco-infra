from cStringIO import StringIO
from liminfra.sync.syncd import skip_queued_items
from liminfra.members.models import User
import subprocess

def init(commands):
	commands.register(update_domain_map)

def update_domain_map(se):
	skip_queued_items(se.daemon, se.command, se.arguments)
	# domain = Domain.objects.get(name=se.get_parameters())
	domain = name=se.get_parameters()
	data = postfix_generate_virtual_map(domain)
	fn = '/usr/local/etc/postfix/virtual/'+ domain
	with open(fn, 'w') as fh:
		fh.write(data)
	subprocess.check_call(['postmap', fn])

def postfix_generate_virtual_map(domain):
	out = StringIO();
	if domain == 'leden.limesco.nl':
		for a in User.objects.filter():
			out.write("%s@%s %s\n" % (a.username, domain, a.email))
	return out.getvalue()
