from liminfra.sync.models import SpoolEntry

def add_spool_entry(daemon, command, arguments=None):
	se = SpoolEntry(daemon=daemon, command=command)
	se.set_parameters(arguments)
	se.save()
