# This resource is used to create/delete a log entry in the archive.log
# log_location is used to specify the location of archive.log and log_record
# is the string to be added to the archive.log.

actions :add, :remove

attribute :name, name_attribute: true, kind_of: String
attribute :log_record,       kind_of: String
attribute :log_location,     kind_of: String

def initialize(*args)
  super
end
