# Library for downloading archive log from master and scanning it to get appropriate fields.

module ArchiveLog
  $contentDict = Hash.new

  def self.getLog(run_context, node)
    # Downloading archive log from custom repositry.
    archive_path = "#{node['buildServer']['download_location']}/archive.log"
    archiveFile = Chef::Resource::RemoteFile.new(archive_path, run_context)
    archiveFile.source("#{node['buildServer']['repo_url']}/archives/archive.log")
    archiveFile.run_action(:create)

    # Reading downloaded archive file and creating a global hash with
    # key as name_version and value holding an array of extensions
    begin
      fields = []
      f = File.open(archive_path, "r")
      f.each_line do |line|
        temp = line.split(',')
        fields.push(temp)
      end
      fields.each do |field|
        key = field[0] + '_' + field[1]
        if $contentDict.has_key?(key)
           $contentDict[key].push(field[5])
        else
          $contentDict[key] = [ field[5] ]
        end
      end
    rescue IOError, StandardError => e
      puts "Error: #{e.message}"
    ensure
      f.close
    end
  end

  def self.getExtension(name, version)
     # Getting extension for a given package for a particular version
     key = name + '_' + version
     begin
       $contentDict.fetch(key)[0]
     rescue KeyError, StandardError => e
       puts "Error: #{e.message}"
     end
  end

end
