Introduction
=======
The OpenStack Horizon UI provides a Django-based application that controls OpenStack clouds.
It is an extremely extensible, customizable, and testable framework that has been developed
by a large community of knowledgeable and passionate open source developers..

Our supervessel_cloud_mgr is build on OpenStack Horizon.

Current Capabilities
========
 - Create and deploy autoport cluster in supervessel automatically. 6 virtual nodes will be created:
     - autoport driver
     - jenkins master
     - jenkins slave on rhel x86
     - jenkins slave on rhel power
     - jenkins slave on ubuntu x86
     - jenkins slave on ubuntu power

Dependencies
========
Please refer to [1]

Specific code for Autoport
========
(1) def handle() in /supervessel_cloud_mgr/openstack_dashboard/dashboards/project/stacks/forms.py
   autoport.yaml processing
(2) /supervessel_cloud_mgr/openstack_dashboard/dashboards/project/stacks/templates/_lauch.html
   page about autoport cluster description
For more details please refer to [2]

Running
========
In SuperVessel environment,open the URL in browsers:
   https://bigdata.ptopenlab.com:8800/autoport/

References
=======
[1] Quickstart http://docs.openstack.org/developer/horizon/quickstart.html
[2] Tutorial: Building a Dashboard using Horizon, http://docs.openstack.org/developer/horizon/topics/tutorial.html
