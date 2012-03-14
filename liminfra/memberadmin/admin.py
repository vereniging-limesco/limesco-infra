from django.contrib import admin
from liminfra.memberadmin.models import Member, Group, Seat

class MemberAdmin(admin.ModelAdmin):
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

admin.site.register(Member, MemberAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Seat, SeatAdmin)
