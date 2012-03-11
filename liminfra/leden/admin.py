from django.contrib import admin
from django.contrib.auth.models import User, Group
from liminfra.leden.models import Member, Seat

class MemberAdmin(admin.ModelAdmin):
	list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
	list_filter = ('is_staff', 'is_superuser', 'is_active')
	search_fields = ('username', 'first_name', 'last_name', 'email')
	ordering = ('username', )

class SeatAdmin(admin.ModelAdmin):
	list_display = ('name', 'group', 'member')
	list_filter = ('name',)
	search_fields = ('name', 'humanName', 'description')
	ordering = ('group', 'name')

admin.site.unregister(User)
admin.site.register(Member, MemberAdmin)
admin.site.register(Seat, SeatAdmin)
