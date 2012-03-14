from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from liminfra.support.models import *
from liminfra.support.forms import CreateTicketForm

@login_required
def overview(request):
	user = request.user.user
	my_tickets = list(Ticket.objects.filter(asker=user))
	assigned_tickets = list(Ticket.objects.filter(assignee=user))
	if len(my_tickets) == 0:
		my_tickets = False
	if len(assigned_tickets) == 0:
		assigned_tickets = False
	return render_to_response('support/overview.html', {'my_tickets': my_tickets, 'assigned_tickets': assigned_tickets}, context_instance=RequestContext(request))

@login_required
def create_ticket(request):
	if request.method == 'POST':
		form = CreateTicketForm(request.POST)
		if form.is_valid():
			t = form.save(commit=False)
			t.asker = request.user.user
			t.assignee = None
			t.waitsfor = 'assignee'
			msg = TicketMessage(person=request.user.user, message=request.POST['initial_message'])
			t.save()
			msg.ticket = t
			msg.save()
			return HttpResponseRedirect(reverse('view-ticket', kwargs={'id': t.id}))
	else:
		form = CreateTicketForm()

	return render_to_response('support/create_ticket.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def view_ticket(request, id):
	user = request.user.user
	try:
		t = Ticket.objects.get(id=id)
	except Ticket.DoesNotExist:
		raise Http404
	is_asker = (t.asker_id == user.id)
	is_assignee = (t.assignee_id == user.id)
	is_moderator = False
	be_verbose = ('verbose' in request.GET)
	if request.method == 'POST':
		if is_assignee and 'faqreply' in request.POST and request.POST['faqreply'] != '':
			t.add_faqreply(user, save=False)
		elif not is_assignee and 'complain' in request.POST and request.POST['complaint'] != '':
			t.file_complaint(user, request.POST['complaint'], save=False)
		elif is_asker and 'accept' in request.POST:
			t.accept_resolution(user, save=False)
		else:
			if request.POST['message'] != '':
				t.add_message(user, request.POST['message'], save=False)
			if is_assignee and 'backtoyou' in request.POST:
				t.waitsfor = 'asker'
			if is_assignee and 'mark_spam' in request.POST:
				t.mark_spam(user, save=False)
			elif is_assignee and 'mark_invalid' in request.POST:
				t.mark_invalid(user, save=False)
			elif is_assignee and 'abandon' in request.POST:
				t.abandon(user, save=False)
		t.save()
		return HttpResponseRedirect(reverse('view-ticket', kwargs={'id': t.id}))
	objhistory = []
	for type in (TicketMessage, TicketChange, TicketFAQReply, TicketBounty, TicketComplaint, TicketAbandon):
		for entry in type.objects.filter(ticket=t):
			objhistory.append(entry)
	if be_verbose:
		for entry in TicketTake.objects.filter(ticket=t):
			objhistory.append(entry)
	objhistory.sort(key=lambda x: x.date, reverse=True)
	new_category = t.category
	new_state = t.state
	new_private = t.private
	new_level = t.level
	new_assignee = t.assignee
	history = []
	for obj in objhistory:
		item = {
			'person': obj.person,
			'date': obj.date,
			'type': obj.__class__.__name__,
		}
		if isinstance(obj, TicketChange):
			if not obj.old_category is None:
				item['category'] = [obj.old_category, new_category]
				new_category = obj.old_category
			if not obj.old_state is None:
				item['state'] = [obj.old_state, new_state]
				new_state = obj.old_state
			if not obj.old_private is None:
				item['private'] = [obj.old_private, new_private]
				new_private = obj.old_private
			if not obj.old_level is None:
				item['level'] = [obj.old_level, new_level]
				new_level = obj.old_level
			if not obj.old_assignee is None:
				item['assignee'] = [obj.old_assignee, new_assignee]
				new_assignee = obj.old_assignee
		elif isinstance(obj, TicketMessage):
			item['message'] = obj.message
		elif isinstance(obj, TicketComplaint):
			item['complaint'] = obj.message
			item['against'] = obj.against
			item['new_assignee'] = new_assignee = None
		elif isinstance(obj, TicketFAQReply):
			item['question'] = obj.faq.question
			item['answer'] = obj.faq.answer
		elif isinstance(obj, TicketBounty):
			item['value'] = obj.value.question
		elif isinstance(obj, TicketTake):
			item['chosen'] = obj.chosen
		elif isinstance(obj, TicketAbandon):
			item['new_level'] = new_level = obj.old_level
			if not be_verbose:
				# Prevent being added to history
				continue
		history.append(item)
	history.reverse()
	print history
	return render_to_response('support/ticket.html', {'t': t, 'history': history, 'is_asker': is_asker, 'is_assignee': is_assignee, 'is_moderator': is_moderator}, context_instance=RequestContext(request))
