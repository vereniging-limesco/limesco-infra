from django.contrib import admin
import django.contrib.auth.models
from liminfra.portal.models import User, Group, Seat

class UserAdmin(admin.ModelAdmin):
	list_display = ('username', 'email', 'first_name', 'last_name', 'public_name')
	list_filter = ('is_active', )
	search_fields = ('username', 'first_name', 'last_name', 'public_name', 'email')
	ordering = ('username', )

class GroupAdmin(admin.ModelAdmin):
	list_display = ('name', 'humanName')
	list_filter = ('name', )
	search_fields = ('name', 'humanName')
	ordering = ('name', )

class SeatAdmin(admin.ModelAdmin):
	list_display = ('name', 'group', 'member')
	list_filter = ('name',)
	search_fields = ('name', 'humanName', 'description')
	ordering = ('group', 'name')

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Seat, SeatAdmin)
admin.site.unregister(django.contrib.auth.models.User)
admin.site.unregister(django.contrib.auth.models.Group)
