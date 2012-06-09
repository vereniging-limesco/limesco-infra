from liminfra import settings
from liminfra.sync.syncd import skip_queued_items
from liminfra.sync.util import add_spool_entry
import subprocess
import os.path

def init(commands):
	commands.register(create_user)
	commands.register(change_password)

def create_user(se):
	username, password = se.get_parameters()
	subprocess.check_call(['php', 'maintenance/createAndPromote.php', username, password], cwd=settings.MEDIAWIKI_PATH)

def change_password(se):
	username, password = se.get_parameters()
	subprocess.check_call(['php', 'maintenance/changePassword.php', '--user', user, '--password', password], cwd=settings.MEDIAWIKI_PATH)
