from django.contrib import admin
from liminfra.sync.models import SpoolEntry

def requeue(modeladmin, request, queryset):
	queryset.update(state='queued')
requeue.short_description = "Requeue selected entries"

def block(modeladmin, request, queryset):
	queryset.update(state='blocked')
block.short_description = "Block selected entries"

class SpoolEntryAdmin(admin.ModelAdmin):
	list_display = ('daemon', 'state', 'command')
	list_filter = ('daemon', 'state')
	actions = [requeue,block]

admin.site.register(SpoolEntry, SpoolEntryAdmin)
