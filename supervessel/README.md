Current Capabilities
========
 - create and deploy autoport cluster in supervessel automatically. 6 virtual nodes will be created:
     - autoport driver
     - jenkins master
     - jenkins slave on rhel x86
     - jenkins slave on rhel power
     - jenkins slave on ubuntu x86
     - jenkins slave on ubuntu power


Dependencies
========
Install [pip](https://pip.pypa.io/en/latest/installing.html) and then run these commands to install dependencies:

    pip install Flask
    pip install python-keystoneclient
    pip install python-heatclient

Running
========
After installing dependencies, simply clone the repo and run:

    python main.py

Navigate to http://127.0.0.1:5000/autoport/ to access the app.
