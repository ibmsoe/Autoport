# Downloading archive log from master and scanning it to get appropriate fields.

Chef::Recipe.send(:include, ArchiveLog)
ArchiveLog.getLog(run_context, node)
