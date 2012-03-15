from liminfra.portal.models import User

def init(commands):
	commands.register(add_user)
	commands.register(update_user)
	commands.register(remove_user)

def add_user(se):
	info = se.get_parameters()
	usr = User(username=info['username'], password=info['password'], email=info['username'] +'@leden.limesco.nl', public_name=info['username'], is_male=info['is_male'])
	usr.save()

def update_user(se):
	info = se.get_parameters()
	usr = User.objects.get(username=info['username'])
	usr.password = info['password']
	usr.public_name = info['public_name']
	usr.is_male = info['is_male']
	usr.is_active = info['is_active']
	usr.save()

def remove_user(se):
	info = se.get_parameters()
	usr = User.objects.get(username=info['username'])
	usr.delete()
