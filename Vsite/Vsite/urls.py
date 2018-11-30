from django.contrib import admin
from django.urls import path
from django.conf.urls import handler404, handler500
import intro.views

urlpatterns = [
	path('', intro.views.intro),
	path('signup/', intro.views.signup),
	path('users/', intro.views.user_list),
	path('thanks/', intro.views.thanks),
	path('admin/', admin.site.urls)
]

handler404 = intro.views.handler404
handler500 = intro.views.handler500
