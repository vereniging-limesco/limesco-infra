from liminfra.members.models import User

class AuthBackend:
	def authenticate(self, username=None, password=None):
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			return None
		if not user.check_password(password):
			return None
		return user

	def get_user(self, pk):
		try:
			return User.objects.get(pk=pk)
		except User.DoesNotExist:
			return None
