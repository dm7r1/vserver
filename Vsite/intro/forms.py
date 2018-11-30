from django import forms


class SignUpForm(forms.Form):
	login = forms.CharField(max_length=20)
	password1 = forms.CharField(max_length=32)
	password2 = forms.CharField(max_length=32)