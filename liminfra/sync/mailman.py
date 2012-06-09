from cStringIO import StringIO
from liminfra import settings
from liminfra.sync.syncd import skip_queued_items
from liminfra.sync.util import add_spool_entry
import subprocess
import os.path

import Mailman
import Mailman.Utils
import Mailman.UserDesc
import Mailman.MemberAdaptor
from Mailman import MailList, mm_cfg

settings.MAILMAN_PATH = '/usr/local/mailman/'
settings.MAILMAN_DEFAULT_OWNER = 'bofh@lists.limesco.nl'

def init(commands):
	commands.register(get_state)
	commands.register(add_list_members)
	commands.register(remove_list_members)
	commands.register(update_list_member_settings)
	# commands.register(update_list_settings)
	commands.register(create_list)
	# commands.register(delete_list)
	# commands.register(sync_lists)
	# commands.register(sync_list_members)

def get_state(se):
	list, reply_daemon, reply_cmd = se.get_parameters()
	ml = MailList.MailList(list, lock=False)
	ret = []
	ret.append(list)
	ret.append(ml.members.keys())
	add_spool_entry(reply_daemon, reply_cmd, ret)

def add_list_members(se):
	name, domain, addresses = se.get_parameters()
	# domain = Domain.objects.get(name=domain)
	# lst = List.objects.get(name=name, domain=domain)
	# nomail_list = map(lambda x: x.email, ListMember.objects.filter(list=lst, email__in=addresses, nomail=True))
	ml = MailList.MailList(name)
	try:
		for em in addresses:
			pw = Mailman.Utils.MakeRandomPassword()
			desc = Mailman.UserDesc.UserDesc(em, '', pw, False)
			ml.ApprovedAddMember(desc, False, False)
		# for em in nomail_list:
		#	ml.setDeliveryStatus(em, Mailman.MemberAdaptor.BYADMIN)
	finally:
		ml.Save()
		ml.Unlock()

def remove_list_members(se):
	name, domain, addresses = se.get_parameters()
	# domain = Domain.objects.get(name=domain)
	# lst = List.objects.get(name=name, domain=domain)
	ml = MailList.MailList(name)
	try:
		for em in addresses:
			ml.ApprovedDeleteMember(em, admin_notif=False, userack=False)
	finally:
		ml.Save()
		ml.Unlock()

def update_list_member_settings(se):
	"""
	name, domain, addresses = se.get_parameters()
	# domain = Domain.objects.get(name=domain)
	# lst = List.objects.get(name=name, domain=domain)
	lms = ListMember.objects.filter(list=lst, email__in=addresses)
	ml = MailList.MailList(lst.name)
	try:
		for lm in lms:
			old = ml.getDeliveryStatus(lm.email)
			if lm.nomail:
				new = Mailman.MemberAdaptor.BYADMIN
			else:
				new = Mailman.MemberAdaptor.ENABLED
			if old != new:
				ml.setDeliveryStatus(lm.email, new)
	finally:
		ml.Save()
		ml.Unlock()
	"""
	pass

def update_list_settings(se):
	name, domain = se.get_parameters()
	domain = Domain.objects.get(name=domain)
	lst = List.objects.get(name=name, domain=domain)
	mods = map(lambda x: x.email, list(ListModerator.objects.filter(list=lst)))
	ml = MailList.MailList(lst.name)
	try:
		ml.moderator = mods
		if lst.moderate_members:
			default_member_moderation = 1
		else:
			default_member_moderation = 0
		if lst.moderate_nonmembers:
			ml.generic_nonmember_action = 1
		else:
			ml.generic_nonmember_action = 0
		if lst.emergency:
			ml.emergency = 1
		else:
			ml.emergency = 0
		for m in ml.getMembers():
			ml.setMemberOption(m, mm_cfg.Moderate, lst.moderate_members)
	finally:
		ml.Save()
		ml.Unlock()

def create_list(se):
	name, domain = se.get_parameters()
	newlist = os.path.join(settings.MAILMAN_PATH, 'bin/newlist')
	pw = Mailman.Utils.MakeRandomPassword()
	subprocess.check_call([newlist, '-q', name, settings.MAILMAN_DEFAULT_OWNER, pw])
	ml = MailList.MailList(name)
	try:
		ml.send_reminders = 0
		ml.send_welcome_msg = False
		ml.max_message_size = 0
		ml.subscribe_policy = 3
		ml.unsubscribe_policy = 0
		ml.private_roster = 2
		ml.require_explicit_destination = 0
		ml.max_num_recipients = 0
		ml.archive = 0
		ml.archive_private = 1
		ml.generic_nonmember_action = 0
	finally:
		ml.Save()
		ml.Unlock()

def delete_list(se):
	add_spool_entry('postfix', 'update_domain_map', domain.name)
	raise NotImplemented

def sync_list_members(se):
	skip_queued_items(se.daemon, se.command, se.arguments)
	domain = Domain.objects.get(name=se.get_parameter(1))
	lst = List.objects.get(name=se.get_parameter(0), domain=domain)
	members = dict(map(lambda l: (l.email, l), ListMember.objects.filter(list=lst)))
	ml = MailList.MailList(lst.name, lock=False)
	desired = frozenset(members.keys())
	current = frozenset(ml.getMembers())
	del_set = current - desired
	if del_set:
		add_spool_entry('mailman', 'remove_list_members', [lst.name, domain.name, list(del_set)])
	add_set = desired - current
	if add_set:
		add_spool_entry('mailman', 'add_list_members', [lst.name, domain.name, list(add_set)])
	change_set = set()
	for m in desired & current:
		cur = (ml.getDeliveryStatus(m) == Mailman.MemberAdaptor.BYADMIN)
		des = members[m].nomail
		if cur != des:
			change_set.add(m)
	if change_set:
		add_spool_entry('mailman', 'update_list_member_settings', [lst.name, domain.name, list(change_set)])

def sync_lists(se):
	skip_queued_items(se.daemon, se.command, se.arguments)
	domain = Domain.objects.get(name=se.get_parameter(0))
	list_objects = set(List.objects.filter(domain=domain))
	desired = frozenset(map(lambda x: x.name, list_objects))
	current = frozenset(Mailman.Utils.list_names())
	for l in current - desired:
		add_spool_entry('mailman', 'delete_list', [l, domain.name])
	for l in desired - current:
		add_spool_entry('mailman', 'create_list', [l, domain.name])
	for l in desired & current:
		add_spool_entry('mailman', 'sync_list_members', [l, domain.name])
		add_spool_entry('mailman', 'update_list_settings', [l, domain.name])

if __name__ == '__main__':
	ml = MailList.MailList('leden', lock=False)
	print ml.members.keys()
