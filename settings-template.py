#  ########################################################################################
#  IMPORTANT: This file should be renamed settings.py and then modified before use.       #
#  ########################################################################################


#  Rocky Version
VERSION = "0.2.0"

#  DNS Name Servers
ROUTER_NAME_SERVERS = ["91.103.0.1", "91.103.0.2", "8.8.8.8", "2a02:2078:cb01::2"]

#  Public Keys
# These keys allow Rocky to log in to the SRX Router(s) to update the network configuration 
# 
ROCKY_RSA = "Place Rocky's public key here"

#  Managed Cloud Infrastructure
# One instance of Rocky can manage multiple clouds and each cloud will consist of one or more regions.
# This configuration describes the cloud infrastructure managed by this instance of Rocky.

clouds  = [
    # First Cloud ...
    {
        'name': 'First Cloud',
        
        # python-cloudcix api settings
        'CLOUDCIX_API_URL' :'https://api.your_first_cloud_url.com/',
        'CLOUDCIX_API_USERNAME': 'rocky@your_first_cloud_url.com',
        'CLOUDCIX_API_PASSWORD': 'Password_Here',
        'CLOUDCIX_API_KEY': 'Get_From_Membership_App',
        'CLOUDCIX_API_VERSION': 2,
        'CLOUDCIX_API_V2_URL': 'https://api.your_first_cloud_url.com/',
        
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
                'name': 'Second Region'
            },
        ],
        
        # SRX settings
        # SSH Keys allow Robots in each region to configure 'their' local SRX Routers. 
        'ROBOT_RSA': "All instances of Robot in a Cloud have the same key pair. Place the public key here ",
        
        # Inbound Access list
        # The management network of this SRXPod is firewalled to block all inbound traffic.
        # Access is allowed to the management network from this list of external Public IPs.
        'MGMT_ACCESS_LIST': {
             #  If this region is managed by an external COP then the IP address ranges of that COP must be allowed in.
             #  If this region contains a COP then evternal access is not required and leave these
             'COP_IPV4' : '255.255.255.255/32',
             'COP_IPV6' : 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128',
             
             #  This region must be monitored by a instance of Rocky and therefore the IP address
             'ROCKY': 'Rocky ipaddress'
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
            'link_subnet': 'X:Y:z::/N',  #  /126 per region minimum
        },
    },
    
    # Second Cloud ...
    {
        "name": 'Second Cloud',
    },
]
