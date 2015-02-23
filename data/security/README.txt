Build artifacts are copied from Jenkins' slave servers to the autoport
server, so a security key pair is needed for this copy.

As a simplification for development purposes, we include a security key
in the source code, so that there is no setup required.  In this way,
each developer may have a private installation of autoport that connects
to a shared Jenkins build server.

If site policy dictates that keys can't be shared by end users or if one
wants to connect to a different Jenkins server, then some of the following 
must be done.  This is end to end procedure.

On the autoport server

    ssh-keygen -P'' -t rsa -f jenkins
    scp jenkins.pub jenkinshost:~

Then connect to the jenkins server (sudo access is required):

    ssh jenkinshost
    sudo cat jenkins.pub > ~jenkins/
    sudo chown jenkins:jenkins ~jenkins/jenkins.pub
    sudo su - jenkins
    mkdir -p .ssh data/test_results data/batch_files
    cat jenkins.pub >> .ssh/authorized_keys

