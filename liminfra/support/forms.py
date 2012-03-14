from django.forms import ModelForm, CharField, Textarea
from liminfra.support.models import Ticket

class CreateTicketForm(ModelForm):
	initial_message = CharField(min_length=1, widget=Textarea)

	class Meta:
		model = Ticket
		fields = ('category', 'private', 'subject')
