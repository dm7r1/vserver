from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from .forms import SignUpForm
from .models import VUser
import re


def intro(request):
	return render(request, 'intro/templates/intro.html')


def handler404(request, exception=None, template_name='404.html'):
	response = render_to_response('intro/templates/404.html', {})
	response.status_code = 404
	return response


def handler500(request, exception=None, template_name='500.html'):
	response = render_to_response('intro/templates/500.html', {})
	response.status_code = 500
	return response


@csrf_protect
def signup(request):
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			mistakes = []
			login = form.cleaned_data["login"]
			password = form.cleaned_data["password2"]
			if not (4 <= len(login) <= 20):
				mistakes.append(("login", "Login length must be in range 4..20 symbols"))
			if re.search("\W", login):
				mistakes.append(("login", "Login must contains only 0..9, a..z, A..Z and _"))
			if not (6 <= len(password) <= 32):
				mistakes.append(("password", "Password length must be in range 6..32 symbols"))
			if re.search("\W", password):
				mistakes.append(("password", "Password must contains only 0..9, a..z, A..Z and _"))
			if not form.cleaned_data["password1"] == form.cleaned_data["password2"]:
				mistakes.append(("password2", "Passwords do not match"))
			if VUser.objects.filter(login=login).exists():
				mistakes.append(("user", "User with such login already exists"))
			if len(mistakes) == 0:
				VUser.makenew(login=login, password=password)
				return HttpResponseRedirect("/thanks/")
			else:
				return render(request, 'intro/templates/signup.html', {"remarks": mistakes}, RequestContext(request))

	return render(request, 'intro/templates/signup.html', {"remarks": []}, RequestContext(request))


def user_list(request):
	return render(request, 'intro/templates/user_list.html', {"users": VUser.objects.all()})


def thanks(request):
	return render(request, 'intro/templates/thanks.html', {})
