import subprocess

from liminfra.sync.syncd import skip_queued_items
from liminfra.sync.util import add_spool_entry
from liminfra.members.models import User, Group

def init(commands):
	commands.register(start_check)
	commands.register(sync_mailman)

def start_check(se):
	for grp in Group.objects.all():
		add_spool_entry('mailman', 'get_state', [grp.name, 'ccd', 'sync_mailman'])
	add_spool_entry('postfix', 'update_domain_map', 'leden.limesco.nl')

def sync_mailman(se):
	name, current = se.get_parameters()
	current = frozenset(current)
	grp = Group.objects.get(name=name)
	desired = frozenset([user.email for user in grp.user_set.all()])
	add = desired - current
	remove = current - desired
	if add:
		add_spool_entry('mailman', 'add_list_members', [name, 'lists.limesco.nl', list(add)])
	if remove:
		add_spool_entry('mailman', 'remove_list_members', [name, 'lists.limesco.nl', list(remove)])
