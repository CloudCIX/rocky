#  #######################################################################
#  This file needs to be modified and renamed settings.py before use.  #
#  ######################################################################


#  Rocky Version
VERSION = "0.2.0"

#  DNS Name Servers
ROUTER_NAME_SERVERS = ["91.103.0.1", "91.103.0.2", "8.8.8.8", "2a02:2078:cb01::2"]

#  Public Keys
# These Keys allow Rocky to change the network configuration on the SRX Routers 
ROCKY_RSA = "Place Rocky's public key here"

#  Managed Cloud Infrastructure
# One instance of Rocky can manage many Clouds and each Cloud can have many regions.
# This configuration describes the Cloud infrastructure managed by this instance of Rocky.

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
        
         # SRX settings
         # These Keys allow Robot to change the network configuration on the SRX Routers 
        'ROBOT_RSA': "All instances of Robot have the same key pair. Place the public key here ",
         # Inbound Access list
         # The management network of this SRXPod is firewalled to block all inbound traffic.
         # Access is allowed to the management network from this list of external Public IPs.
         #  If this region is managed by an external COP then the IP address ranges of that COP must be allowed in.
         #  If this region contains a COP then evternal access is not required and leave these
         #  This region must be monitored by a instance of Rocky and therefore the IP address
         'MGMT_ACCESS_LIST': {
             'COP_IPV4' : '255.255.255.255/32',
             'COP_IPV6' : 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128',
             'ROCKY': 'Rocky ipaddress'
         },
    },
    
    # Second Cloud ...
    {
        "name": 'Second Cloud',
    },
]
