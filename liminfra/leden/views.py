from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response

@login_required
def welcome(request):
	return render_to_response('leden/welcome.html', {}, context_instance=RequestContext(request))
