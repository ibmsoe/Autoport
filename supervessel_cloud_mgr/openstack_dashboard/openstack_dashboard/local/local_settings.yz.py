import os

from django.utils.translation import ugettext_lazy as _

from openstack_dashboard import exceptions

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Required for Django 1.5.
# If horizon is running in production (DEBUG is False), set this
# with the list of host/domain names that the application can serve.
# For more information see:
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
#ALLOWED_HOSTS = ['horizon.example.com', 'localhost']
ALLOWED_HOSTS = ['*']

# Set SSL proxy settings:
# For Django 1.4+ pass this header from the proxy after terminating the SSL,
# and don't forget to strip it from the client's request.
# For more information see:
# https://docs.djangoproject.com/en/1.4/ref/settings/#secure-proxy-ssl-header
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

# If Horizon is being served through SSL, then uncomment the following two
# settings to better secure the cookies from security exploits
USE_SSL = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# Overrides for OpenStack API versions. Use this setting to force the
# OpenStack dashboard to use a specific API version for a given service API.
# NOTE: The version should be formatted as it appears in the URL for the
# service API. For example, The identity service APIs have inconsistent
# use of the decimal point, so valid options would be "2.0" or "3".
# OPENSTACK_API_VERSIONS = {
#     "identity": 3,
#     "volume": 2
# }

# Set this to True if running on multi-domain model. When this is enabled, it
# will require user to enter the Domain name in addition to username for login.
# OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = False

# Overrides the default domain used when running on single-domain model
# with Keystone V3. All entities will be created in the default domain.
# OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default'

# Set Console type:
# valid options would be "AUTO", "VNC", "SPICE" or "RDP"
# CONSOLE_TYPE = "AUTO"

OPENSTACK_CONFIG_BACKEND = {
    'configs': [{'region': 'HangZhou',
                 'internal_ip_id': 'c4610e71-39d8-416b-85fb-6cbb450db8a2',
                 'external_ip_id': 'afc85698-a02c-4256-9201-daa0a34ac311',
                 'management_ip_id': 'd46c5718-e142-43ea-9338-c0a999ee41cf',
                 'vlan_name': 'net_vlan1',
                 'image_admin_email_list': [
                     'bjhtyue@cn.ibm.com',
                     'linzhbj@cn.ibm.com',
                 ],
                 },
                {'region': 'Beijing',
                 'internal_ip_id': '9d8b2e30-1bd2-4bda-b44b-33c09bb45b87',
                 'external_ip_id': 'c24ebbf6-8d64-4dd5-b59d-c9a5d66274c0',
                 'management_ip_id': 'ca699bbc-c793-4a8a-95c3-1ca56f0962d4',
                 'users_use_kvm': [
                     'taufer@udel.edu',
                     'sychen@udel.edu',
                     'sherbein@udel.edu',
                     'aron@udel.edu',
                     'bhargava@udel.edu',
                     'seanmcd@udel.edu',
                     'josem@udel.edu',
                     'zqshi@udel.edu',
                     'kumar@udel.edu',
                     'stevenz@udel.edu',
                     'yyangwin@udel.edu',
                     'adusia@udel.edu',
                     'bjhtyue@cn.ibm.com',
                     'linzhbj@cn.ibm.com',
                     'linzhaolover@163.com',
                     '452949990@qq.com',
                     'openpowerlabtest@163.com',
                     '13681090940@139.com',
                     'hangliu@cn.ibm.com',
                     'luyong@cn.ibm.com',
                     'pengou@cn.ibm.com',
                     'autocf@sohu.com',
                     'supervesseluser@sina.com',
                     'lijianhua@sequoiadb.com',
                 ],
                 'image_admin_email_list': [
                     'bjhtyue@cn.ibm.com',
                     'linzhbj@cn.ibm.com',
                 ],
                 'accelerator_zone': {
                     'capi': 'nova',
                     'pcie': 'accelerator',
                 },
                 'vlan_name': 'net-vlan1'},
                ],
    'user': 'admin',
    'password': 'p0weradm1n',
    'tenant': 'service',
    'users_use_system_quota': [
        'luopingy@cn.ibm.com',
        'bjhtyue@cn.ibm.com',
        'gongyan@163.com',
        'nmaeding@de.ibm.com',
    ],
    'global_instance_quota': 2,
    'capi_quota': 1,
}

PUBLISH_IMAGE_BACKEND = {
    'type_choices': [
        ("basic", _("Basic Image")),
        ("compute", _("Scientific Compute")),
        ("web", _("Web Application Service")),
        ("media", _("Multimedia Service")),
        ("learning", _("Machine Learning"))
    ]
}

TIMEOUT = 5

STACK_BACKEND = {
    'service_type': [
        ("spark", "Spark"),
        ("map_reduce", "Map Reduce (Symphony)"),
    ],
    'node_count': [
        ("1", _("One")),
        ("3", _("Three")),
        ("5", _("Five")),
    ],
    'disk_size': [
        ("20", "20G"),
        ("40", "40G"),
    ],
    'quota': 2
}

OPENSTACK_TYPE_CHOICE_BACKEND = {
    'choices': [{'region': 'HangZhou',
                 'sys_type': [('rhel', 'Red Hat'),
                              ('ubuntu', 'Ubuntu')],
                 'architecture': [('ppc64', 'PowerPC64 Big Endian')],
                 'accelerator_type': [('capi', 'CAPI'),
                                      ('pcie', 'PCIE')],
                 'use_accelerator_choice': [('', _('None')),
                                            ('fpga', _('FPGA Accelerator')),
                                            ('gpu', _('GPU Accelerator'))],
                 },
                {'region': 'Beijing',
                 'sys_type': [
                              ('redflag', _('Red Flag')),
                              ('rhel', 'Red Hat'),
                              ('ubuntu', 'Ubuntu'),
                              ],
                 'architecture': [('ppc64', 'PowerPC64 Big Endian'),
                                  ('ppc64le', 'PowerPC64 Little Endian')],
                 'accelerator_type': [('capi', 'CAPI'),
                                      ('pcie', 'PCIE')],
                 'use_accelerator_choice': [('', _('None')),
                                            ('fpga', _('FPGA Accelerator')),
                                            ('gpu', _('GPU Accelerator'))],
                 },
                ]
}


USER_QUERY_BACKEND = {
    'server': '119.81.170.162',
    'points_transfer_api': '/cloudlab/api/{apikey}/transaction/batch',
    'get_apikey_api': '/cloudlab/api/user/account/%(username)s',
    'preauth_api': '/cloudlab/api/user/account/apikey/%(apikey)s/preauth/%(amount)s',
    'user_points_api': '/cloudlab/api/user/account/%(username)s',
    'add_points': '/cloudlab/api/banker-admin-grp/transaction/give/%(username)s/amount/%(amount)s',
    'apikey': 'f851dab6-c235-440d-8759-6218618c295e',
    'connection_timeout': 3,
}

CUSTOM_INSTANCE_CONFIG = {
    'nics': [
        {"net-id": 'c358f76f-5485-49d7-a94e-988a7518215c', "v4-fixed-ip": ''}
    ],
    'internal_ip_id': '5f5f99e6-1c97-4898-b449-b96e9b718fe9',
    'external_ip_id': '4e9f2849-79f1-44d9-a6d5-c7744a372300',
    'management_ip_id': 'ffe999fa-66df-4c35-a5bc-71a10598eeaf',
    'netvlan': 'net_vlan2',
}

# Default OpenStack Dashboard configuration.
HORIZON_CONFIG = {
    'dashboards': ('project', 'admin', 'settings',),
    'default_dashboard': 'project',
    'user_home': 'openstack_dashboard.views.get_user_home',
    'ajax_queue_limit': 10,
    'auto_fade_alerts': {
        'delay': 3000,
        'fade_duration': 1500,
        'types': ['alert-success', 'alert-info']
    },
    'help_url': "http://docs.openstack.org",
    'exceptions': {'recoverable': exceptions.RECOVERABLE,
                   'not_found': exceptions.NOT_FOUND,
                   'unauthorized': exceptions.UNAUTHORIZED},
}

# Specify a regular expression to validate user passwords.
# HORIZON_CONFIG["password_validator"] = {
#     "regex": '.*',
#     "help_text": _("Your password does not meet the requirements.")
# }

# Disable simplified floating IP address management for deployments with
# multiple floating IP pools or complex network requirements.
# HORIZON_CONFIG["simple_ip_management"] = False

# Turn off browser autocompletion for the login form if so desired.
# HORIZON_CONFIG["password_autocomplete"] = "off"

LOCAL_PATH = '/tmp'

# Set custom secret key:
# You can either set it to a specific value or you can let horizion generate a
# default secret key that is unique on this machine, e.i. regardless of the
# amount of Python WSGI workers (if used behind Apache+mod_wsgi): However, there
# may be situations where you would want to set this explicitly, e.g. when
# multiple dashboard instances are distributed on different machines (usually
# behind a load-balancer). Either you have to make sure that a session gets all
# requests routed to the same dashboard instance or you set the same SECRET_KEY
# for all of them.
from horizon.utils import secret_key
SECRET_KEY = secret_key.generate_or_read_from_file(os.path.join(LOCAL_PATH, '.secret_key_store'))

# We recommend you use memcached for development; otherwise after every reload
# of the django development server, you will have to login again. To use
# memcached set CACHES to something like
CACHES = {
    "default": {
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
            'DB': 1,
            "PICKLE_VERSION": 2,
        }
    }
}
REDIS_TIMEOUT = 7*24*60*60
CUBES_REDIS_TIMEOUT = 60*60
NEVER_REDIS_TIMEOUT = 365*24*60*60

# Send email to the console by default
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Or send them to /dev/null
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Configure these for your outgoing email host
EMAIL_HOST = 'smtp.sendgrid.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'manager@ptopenlab.com'
EMAIL_HOST_PASSWORD = 'ibm123crl'
#EMAIL_USE_TLS = True

# EMAIL_USE_TLS = True
# EMAIL_HOST = 'ap.relay.ibm.com'
# EMAIL_HOST_USER = 'openpower@linux.vnet.ibm.com'
# EMAIL_HOST_PASSWORD = ''
# EMAIL_PORT = 25

# For multiple regions uncomment this configuration, and add (endpoint, title).
# AVAILABLE_REGIONS = [
#     ('http://cluster1.example.com:5000/v2.0', 'cluster1'),
#     ('http://cluster2.example.com:5000/v2.0', 'cluster2'),
# ]
#AVAILABLE_REGIONS = [
#    ('http://192.168.12.24:5000/v2.0', 'HangZhou'),
#    ('http://crl.ptopenlab.com:5000/v2.0', 'Beijing'),
#]

REGIONS = [
    ('http://192.168.12.51:5000/v2.0', 'HangZhou', 'master'),
    ('http://crl.ptopenlab.com:5000/v2.0', 'Beijing', 'slave',
     'https://crl.ptopenlab.com:8800/supernova/api/user/%(user_name)s',
     'https://crl.ptopenlab.com:8800/supernova/security',
     ),
]
# MICHAEL HINES MODIFIED
OPENSTACK_HOST = "192.168.12.51"
OPENSTACK_ENDPOINT_TYPE = "publicURL"
OPENSTACK_KEYSTONE_URL = "http://%s:5000/v2.0" % OPENSTACK_HOST
OPENSTACK_KEYSTONE_DEFAULT_ROLE = "_member_"

# Disable SSL certificate checks (useful for self-signed certificates):
# OPENSTACK_SSL_NO_VERIFY = True

# The CA certificate to use to verify SSL connections
# OPENSTACK_SSL_CACERT = '/path/to/cacert.pem'

# The OPENSTACK_KEYSTONE_BACKEND settings can be used to identify the
# capabilities of the auth backend for Keystone.
# If Keystone has been configured to use LDAP as the auth backend then set
# can_edit_user to False and name to 'ldap'.
#
# TODO(tres): Remove these once Keystone has an API to identify auth backend.
OPENSTACK_KEYSTONE_BACKEND = {
    'name': 'native',
    'can_edit_user': True,
    'can_edit_group': True,
    'can_edit_project': True,
    'can_edit_domain': True,
    'can_edit_role': True
}

#Setting this to True, will add a new "Retrieve Password" action on instance,
#allowing Admin session password retrieval/decryption.
#OPENSTACK_ENABLE_PASSWORD_RETRIEVE = False

# The Xen Hypervisor has the ability to set the mount point for volumes
# attached to instances (other Hypervisors currently do not). Setting
# can_set_mount_point to True will add the option to set the mount point
# from the UI.
OPENSTACK_HYPERVISOR_FEATURES = {
    'can_set_mount_point': False,
    'can_set_password': False,
}

# The OPENSTACK_NEUTRON_NETWORK settings can be used to enable optional
# services provided by neutron. Options currently available are load
# balancer service, security groups, quotas, VPN service.
OPENSTACK_NEUTRON_NETWORK = {
    'enable_lb': False,
    'enable_firewall': False,
    'enable_quotas': True,
    'enable_vpn': False,
    # The profile_support option is used to detect if an external router can be
    # configured via the dashboard. When using specific plugins the
    # profile_support can be turned on if needed.
    'profile_support': None,
    #'profile_support': 'cisco',
}

# The OPENSTACK_IMAGE_BACKEND settings can be used to customize features
# in the OpenStack Dashboard related to the Image service, such as the list
# of supported image formats.
# OPENSTACK_IMAGE_BACKEND = {
#     'image_formats': [
#         ('', ''),
#         ('aki', _('AKI - Amazon Kernel Image')),
#         ('ami', _('AMI - Amazon Machine Image')),
#         ('ari', _('ARI - Amazon Ramdisk Image')),
#         ('iso', _('ISO - Optical Disk Image')),
#         ('qcow2', _('QCOW2 - QEMU Emulator')),
#         ('raw', _('Raw')),
#         ('vdi', _('VDI')),
#         ('vhd', _('VHD')),
#         ('vmdk', _('VMDK'))
#     ]
# }

# The IMAGE_CUSTOM_PROPERTY_TITLES settings is used to customize the titles for
# image custom property attributes that appear on image detail pages.
IMAGE_CUSTOM_PROPERTY_TITLES = {
    "architecture": _("Architecture"),
    "kernel_id": _("Kernel ID"),
    "ramdisk_id": _("Ramdisk ID"),
    "image_state": _("Euca2ools state"),
    "project_id": _("Project ID"),
    "image_type": _("Image Type")
}

# The IMAGE_RESERVED_CUSTOM_PROPERTIES setting is used to specify which image
# custom properties should not be displayed in the Image Custom Properties
# table.
IMAGE_RESERVED_CUSTOM_PROPERTIES = []

# OPENSTACK_ENDPOINT_TYPE specifies the endpoint type to use for the endpoints
# in the Keystone service catalog. Use this setting when Horizon is running
# external to the OpenStack environment. The default is 'publicURL'.
#OPENSTACK_ENDPOINT_TYPE = "publicURL"

# SECONDARY_ENDPOINT_TYPE specifies the fallback endpoint type to use in the
# case that OPENSTACK_ENDPOINT_TYPE is not present in the endpoints
# in the Keystone service catalog. Use this setting when Horizon is running
# external to the OpenStack environment. The default is None.  This
# value should differ from OPENSTACK_ENDPOINT_TYPE if used.
#SECONDARY_ENDPOINT_TYPE = "publicURL"

# The number of objects (Swift containers/objects or images) to display
# on a single page before providing a paging element (a "more" link)
# to paginate results.
API_RESULT_LIMIT = 1000
API_RESULT_PAGE_SIZE = 10

# The timezone of the server. This should correspond with the timezone
# of your entire OpenStack installation, and hopefully be in UTC.
TIME_ZONE = "Asia/Shanghai"

# When launching an instance, the menu of available flavors is
# sorted by RAM usage, ascending. If you would like a different sort order,
# you can provide another flavor attribute as sorting key. Alternatively, you
# can provide a custom callback method to use for sorting. You can also provide
# a flag for reverse sort. For more info, see
# http://docs.python.org/2/library/functions.html#sorted
# CREATE_INSTANCE_FLAVOR_SORT = {
#     'key': 'name',
#      # or
#     'key': my_awesome_callback_method,
#     'reverse': False,
# }

# The Horizon Policy Enforcement engine uses these values to load per service
# policy rule files. The content of these files should match the files the
# OpenStack services are using to determine role based access control in the
# target installation.

# Path to directory containing policy.json files
#POLICY_FILES_PATH = os.path.join(ROOT_PATH, "conf")
# Map of local copy of service policy files
#POLICY_FILES = {
#    'identity': 'keystone_policy.json',
#    'compute': 'nova_policy.json',
#    'volume': 'cinder_policy.json',
#    'image': 'glance_policy.json',
#}

# Trove user and database extension support. By default support for
# creating users and databases on database instances is turned on.
# To disable these extensions set the permission here to something
# unusable such as ["!"].
# TROVE_ADD_USER_PERMS = []
# TROVE_ADD_DATABASE_PERMS = []
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'custom_resource',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '123456',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

LOGGING = {
    'version': 1,
    # When set to True this will disable all logging except
    # for loggers specified in this configuration dictionary. Note that
    # if nothing is specified here and disable_existing_loggers is True,
    # django.db.backends will still log unless it is disabled explicitly.
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(filename)s %(funcName)s %(lineno)d %(message)s',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            # Set the level to "DEBUG" for verbose output logging.
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # Logging from django.db.backends is VERY verbose, send to null
        # by default.
        'django.db.backends': {
            'handlers': ['null'],
            'propagate': False,
        },
        'requests': {
            'handlers': ['null'],
            'propagate': False,
        },
        'horizon': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'openstack_dashboard': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'novaclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'cinderclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'keystoneclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'glanceclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'neutronclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'heatclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'ceilometerclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'troveclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'swiftclient': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'openstack_auth': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'nose.plugins.manager': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'iso8601': {
            'handlers': ['null'],
            'propagate': False,
        },
    }
}

# 'direction' should not be specified for all_tcp/udp/icmp.
# It is specified in the form.
SECURITY_GROUP_RULES = {
    # 'all_tcp': {
        # 'name': 'ALL TCP',
        # 'ip_protocol': 'tcp',
        # 'from_port': '1',
        # 'to_port': '65535',
    # },
    # 'all_udp': {
        # 'name': 'ALL UDP',
        # 'ip_protocol': 'udp',
        # 'from_port': '1',
        # 'to_port': '65535',
    # },
    # 'all_icmp': {
        # 'name': 'ALL ICMP',
        # 'ip_protocol': 'icmp',
        # 'from_port': '-1',
        # 'to_port': '-1',
    # },
    'ssh': {
        'name': 'SSH',
        'ip_protocol': 'tcp',
        'from_port': '22',
        'to_port': '22',
    },
    'smtp': {
        'name': 'SMTP',
        'ip_protocol': 'tcp',
        'from_port': '25',
        'to_port': '25',
    },
    'dns': {
        'name': 'DNS',
        'ip_protocol': 'tcp',
        'from_port': '53',
        'to_port': '53',
    },
    'http': {
        'name': 'HTTP',
        'ip_protocol': 'tcp',
        'from_port': '80',
        'to_port': '80',
    },
    'pop3': {
        'name': 'POP3',
        'ip_protocol': 'tcp',
        'from_port': '110',
        'to_port': '110',
    },
    'imap': {
        'name': 'IMAP',
        'ip_protocol': 'tcp',
        'from_port': '143',
        'to_port': '143',
    },
    'ldap': {
        'name': 'LDAP',
        'ip_protocol': 'tcp',
        'from_port': '389',
        'to_port': '389',
    },
    'https': {
        'name': 'HTTPS',
        'ip_protocol': 'tcp',
        'from_port': '443',
        'to_port': '443',
    },
    'smtps': {
        'name': 'SMTPS',
        'ip_protocol': 'tcp',
        'from_port': '465',
        'to_port': '465',
    },
    'imaps': {
        'name': 'IMAPS',
        'ip_protocol': 'tcp',
        'from_port': '993',
        'to_port': '993',
    },
    'pop3s': {
        'name': 'POP3S',
        'ip_protocol': 'tcp',
        'from_port': '995',
        'to_port': '995',
    },
    'ms_sql': {
        'name': 'MS SQL',
        'ip_protocol': 'tcp',
        'from_port': '1433',
        'to_port': '1433',
    },
    'mysql': {
        'name': 'MYSQL',
        'ip_protocol': 'tcp',
        'from_port': '3306',
        'to_port': '3306',
    },
    'rdp': {
        'name': 'RDP',
        'ip_protocol': 'tcp',
        'from_port': '3389',
        'to_port': '3389',
    },
}

FLAVOR_EXTRA_KEYS = {
    'flavor_keys': [
        ('quota:read_bytes_sec', _('Quota: Read bytes')),
        ('quota:write_bytes_sec', _('Quota: Write bytes')),
        ('quota:cpu_quota', _('Quota: CPU')),
        ('quota:cpu_period', _('Quota: CPU period')),
        ('quota:inbound_average', _('Quota: Inbound average')),
        ('quota:outbound_average', _('Quota: Outbound average')),
    ]
}
