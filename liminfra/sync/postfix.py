from cStringIO import StringIO
from knds.base.models import Domain
from knds.mail.models import Alias, List
from knds.sync.syncd import skip_queued_items
import subprocess

def init(commands):
	commands.register(update_domain_map)

def update_domain_map(se):
	skip_queued_items(se.daemon, se.command, se.arguments)
	domain = Domain.objects.get(name=se.get_parameters())
	data = postfix_generate_virtual_map(domain)
	fn = '/etc/postfix/virtual/'+ domain.name
	with open(fn, 'w') as fh:
		fh.write(data)
	subprocess.check_call(['postmap', fn])

def postfix_generate_virtual_map(domain):
	pmap = {}
	for a in Alias.objects.filter(domain=domain):
		if a.source not in pmap:
			pmap[a.source] = []
		pmap[a.source].append(a.target)
	for l in List.objects.filter(domain=domain):
		if l.name not in pmap:
			pmap[l.name] = []
		pmap[l.name].append(l.name +"@lists.knds.karpenoktem.nl")
	out = StringIO();
	for source, targets in pmap.items():
		out.write("%s %s\n" % (source, " ".join(targets)))
	return out.getvalue()
