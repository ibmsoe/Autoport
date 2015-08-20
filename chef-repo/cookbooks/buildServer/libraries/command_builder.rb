# Library method to get appropriate command based on extension.
module CommandBuilder
    def self.command(extension, run_context)
      # Inputs: extension: archive file format
      #         run_context: current nodes metadata utilized during chef-recipe run.
      # Returns: command: string to be used while extracting archive file.      
      case extension
      when /^(.tar)$/          then command = "tar -xf"
      when /^(.tar.gz|.tgz)$/  then command = "tar -xzf"
      when /^(.tar.bz2|.tbz)$/ then command = "tar -xjf"
      when /^(.tar.xz|.txz)$/  then command = "tar -xJf"
      when '.zip'
        package = Chef::Resource::Package.new('unzip', run_context)
        package.run_action(:install)
        command = 'unzip'
      end
      command
    end
end
