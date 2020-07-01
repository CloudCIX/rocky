#########################################################################################
# IMPORTANT: This file should be copied to setting.py and then completed before use     #
#########################################################################################


#  Rocky Version
VERSION = '0.3.4'

# Path to json file containing hostnames, ip addresses and credentials for monitoring
HOSTS = 'file.json'

# Path to where ports files will be saved
PORTS_PATH = 'path/ports/'

#  DNS Name Servers - List of stringed DNS IPs
ROUTER_NAME_SERVERS = ['8.8.8.8', '1.1.1.1']

#  Public Keys
# These keys allow Rocky and Robot to log in to the SRX Router(s) to update the network configuration
# Rocky RSA
ROCKY_RSA = ''
# Robot RSA
ROBOT_RSA = ''

# Administrator encrypted password (sha256)
ADMINISTRATOR_ENCRYP_PASS = ''

# api user with limited access
API_USER_PASS = 'Ap1S3rVIcE!1'

# Radius server
RADIUS_SERVER_ADDRESS = ''
# hashed password
RADIUS_SERVER_SECRET = ''

# Network Device Repository Path
DEVICE_CONFIG_PATH = 'path/repo/'

#  Managed Cloud Infrastructure
# One instance of Rocky can manage multiple clouds and each cloud will consist of one or more regions.
# This configuration describes the cloud infrastructure managed by this instance of Rocky.
# Monitoring and Provisioning servers needs access to the cloud infrastructure.

# Inbound Access list
# The management network of this SRXPod is firewalled to block all inbound traffic.
# Access is allowed to the management network from this list of external Public IPs.
MAP_ACCESS_LIST = [
    {
        'source_address': '',  # 'any' for all ips
        'destination_address': '',  # 'any' for all ips
        'port': '',  # valid values 1 , 0-655
        'protocol': '',  # 'tcp'/'udp'/'any'
        'description': '',
    },
]


clouds = [
    # First Cloud ...
    {
        'name': 'First Cloud',
        'id': '',

        # python-cloudcix api settings
        'CLOUDCIX_API_URL': '',
        'CLOUDCIX_API_USERNAME': '',
        'CLOUDCIX_API_PASSWORD': '',
        'CLOUDCIX_API_KEY': '',
        'CLOUDCIX_API_VERSION': 2,
        'CLOUDCIX_API_V2_URL': '',

        # COP inbound access list
        # The management network of this SRXPod is firewalled to block all inbound traffic.
        # Access is allowed to the management network from this list of external Public IPs.
        'COP_ACCESS_LIST': [
            {
                'source_address': '',
                'destination_address': '',
                'port': '',
                'protocol': '',
                'description': '',
            },
        ],

        # Pod settings
        'pods': [
            {
                'name': 'name of the cop',
                'id': '',
                'type': 'cop',

                # Network schema
                'IPv4_link_subnet': [
                    #  this is optional, you can leave them as it is.
                    {
                        'address_range': '',
                        'gateway': '',
                    },
                ],
                'IPv4_pod_subnets': [
                    {
                        'address_range': '',
                        'gateway': '',
                    },
                    {
                        'address_range': '',
                        'gateway': '',
                    },
                ],
                'IPv6_link_subnet': [
                    {
                        'address_range': '',
                        'gateway': '',
                    },
                ],
                'IPv6_pod_subnets': [
                    {
                        'address_range': '',
                    },
                ],
                'IPv4_RFC1918_subnets': [
                    {
                        'address_range': '',
                        'gateway': '',
                    },
                ],

                # VPN Tunnel from Support Center to the SRXPOD for management.
                'vpns': [],

            },

            # first region
            {
                'name': 'region name',
                'id': '',
                'type': 'region',

                # Network schema
                'IPv4_link_subnet': [
                    #  this is optional, you can leave them as it is.
                    {
                        'address_range': '',
                        'gateway': '',
                    },
                ],
                'IPv4_pod_subnets': [
                    {
                        'address_range': '',
                        'gateway': '',
                    },
                    {
                        'address_range': '',
                        'gateway': '',
                    },
                ],
                'IPv6_link_subnet': [
                    {
                        'address_range': '',
                        'gateway': '',
                    },
                ],
                'IPv6_pod_subnets': [
                    {
                        'address_range': '',
                    },
                ],
                'IPv4_RFC1918_subnets': [
                    {
                        'address_range': '',
                        'gateway': '',
                    },
                ],

                # VPN Tunnel from Support Center to the SRXPOD for management.
                'vpns': [],
            },

            # Second region
            {
                'name': 'Second Region',
            },
        ],
    },

    # second cloud
    {},
]
