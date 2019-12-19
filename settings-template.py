#  #######################################################################
#  This file needs to be modified and renamed settings.py before use.  #
#  ######################################################################

"""python-cloudcix api settings"""

CLOUDCIX_API_URL = 'https://api.your_url.com/'
CLOUDCIX_API_USERNAME = 'rocky@your_url.com'
CLOUDCIX_API_PASSWORD = 'Password_Here'
CLOUDCIX_API_KEY = 'Get_From_Membership_App'
CLOUDCIX_API_VERSION = 2
CLOUDCIX_API_V2_URL = 'https://api.your_url.com/'

#  Rocky Version
VERSION = "0.2.0"

#  DNS Name Servers
ROUTER_NAME_SERVERS = ["91.103.0.1", "91.103.0.2", "8.8.8.8", "2a02:2078:cb01::2"]

#  Public Keys
# These Keys allow Rocky and Robot to change the network configuration on the  SRX Routers 
ROBOT_RSA = "All instances of Robot have the same key pair. Place the public key here "
ROCKY_RSA = "Place Rocky's public key here"

#  Access list
# The management network is controlled by SRX routers and is firewall protected, so all inbound traffic is blocked.
# An allow policy with the access list ips can enable access to the management network from the outside world.
# The access list can be API servers, deployment servers, etc. where the management hosts (for example,  Robot) need to
# communicate with servers in access list.
# The format is {'name of server': 'ip address/range', ...etc}

MGMT_ACCESS_LIST = {
    "example-management-server": "ip address / range",
    "example-application-server": "ip address / range",
    "rocky-server": "ip address / range"
}
