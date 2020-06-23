#########################################################################################
# IMPORTANT: This file should be copied to setting.py and then completed before use     #
#########################################################################################


#  Rocky Version
VERSION = '0.3.3'

# Path to json file containing hostnames, ip addresses and credentials for monitoring
HOSTS = 'file.json'

# Path to where ports files will be saved
PORTS_PATH = 'path/ports/'

#  DNS Name Servers - List of stringed DNS IPs
ROUTER_NAME_SERVERS = ['8.8.8.8', '1.1.1.1']

#  Public Keys
# These keys allow Rocky to log in to the SRX Router(s) to update the network configuration
#
ROCKY_RSA = ''

# Network Device Repository Path
DEVICE_CONFIG_PATH = 'path/repo/'

#  Managed Cloud Infrastructure
# One instance of Rocky can manage multiple clouds and each cloud will consist of one or more regions.
# This configuration describes the cloud infrastructure managed by this instance of Rocky.

clouds = [
    # First Cloud ...
    {
        'name': 'First Cloud',

        # python-cloudcix api settings
        'CLOUDCIX_API_URL': '',
        'CLOUDCIX_API_USERNAME': '',
        'CLOUDCIX_API_PASSWORD': '',
        'CLOUDCIX_API_KEY': '',
        'CLOUDCIX_API_VERSION': 2,
        'CLOUDCIX_API_V2_URL': '',

        # Region settings
        'region': [
            # First region
            {
                'name': 'First Region',

                # Network schema
                'IPv4': [
                    {
                        'address_range': 'a.b.c.d/e',
                        'gateway': 'a.b.c.x',
                    },
                    {
                        'address_range': 'a.b.c.d/e',
                        'gateway': 'a.b.c.x',
                    },
                ],
            },

            # Second region
            {
                'name': 'Second Region',
            },
        ],

        # Router Auth details
        'ROUTER_USER': 'user',
        'ROUTER_PASSWORD': 'password',

        # SRX settings
        # SSH Keys allow Robots in each region to configure 'their' local SRX Routers.
        'ROBOT_RSA': '',

        # Inbound Access list
        # The management network of this SRXPod is firewalled to block all inbound traffic.
        # Access is allowed to the management network from this list of external Public IPs.
        'MGMT_ACCESS_LIST': {
            #  If this region is managed by an external COP then the IP address ranges of that COP must be allowed in.
            #  If this region contains a COP then external access is not required and leave as below.
            'COP_IPV4': '255.255.255.255/32',
            'COP_IPV6': 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128',

            #  This region must be monitored by a instance of Rocky and therefore the IP address
            'ROCKY': '1',
        },

        # VPN Tunnel from Support Center to the SRXPOD for management.
        'vpns': [],

        # A minimum of /29 IPv4 floating gateway subnet for COP servers
        'IPv4': {
            'address_range': 'a.b.c.d/e',
            'gateway': 'a.b.c.x',
        },

        # A /48 IPv6 routed subnet for Management and Projects
        'IPv6': {
            'address_range': 'A:B:C::/48',
            'link_subnet': 'X:Y:z::/N',  # /126 per region minimum
        },
    },
]
