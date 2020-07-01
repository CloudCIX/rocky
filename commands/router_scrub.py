# stdlib
import json
import re
import traceback
from typing import Any, Dict, Optional
# libs
import netaddr
# local
from bin import RouterMixin, utils
import settings

ADDRESS_NAME_SUB_PATTERN = re.compile(r'[\.\/:]')


class RouterScrub(RouterMixin):

    def run(self):
        self.run_router()

    def prompt(self):
        print()
        utils.colour_print('(colour_cmd)\u250D' + ('\u2501' * 30) + '\u2511')
        utils.colour_print('\u2502' + (' ' * 30) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 12) + '(colour_warning)WARNING(colour_cmd)' + (' ' * 11) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 30) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 2) + '(colour_clear)Deploying a router deletes'
            '(colour_cmd)' + (' ' * 2) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 3) + '(colour_clear)all of the configuration'
            '(colour_cmd)' + (' ' * 3) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 8) + '(colour_clear)on that device'
            '(colour_cmd)' + (' ' * 8) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 30) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 6) + '(colour_clear)Deploying a router'
            '(colour_cmd)' + (' ' * 6) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 5) + '(colour_clear)ALREADY in production'
            '(colour_cmd)' + (' ' * 4) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 2) + '(colour_clear)will cause service outages.'
            '(colour_cmd)' + ' ' + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 3) + '(colour_clear)Make sure you have read'
            '(colour_cmd)' + (' ' * 4) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 4) + '(colour_clear)the "help" and updated'
            '(colour_cmd)' + (' ' * 4) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 3) + '(colour_clear)settings file correctly.'
            '(colour_cmd)' + (' ' * 3) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 5) + '(colour_clear)Press (colour_cmd)Y or y '
            '(colour_clear)to continue.(colour_cmd)' + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 5) + '(colour_clear)Press (colour_cmd)Any key '
            '(colour_clear)to exit.(colour_cmd)' + (' ' * 3) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 30) + '\u2502')
        utils.colour_print(
            '\u2515' + ('\u2501' * 30) + '\u2519(colour_clear)')
        print()

    def run_router(self):
        try:
            self.prompt()

            if input() not in ['Y', 'y']:
                return
            utils.line_break()
            print()

            # loading settings data
            utils.colour_print('Reading the settings file...')
            # validating map_access_list
            utils.colour_print('Validating MAP_ACCESS_LIST ...')
            map_access_list = settings.MAP_ACCESS_LIST
            for firewall in map_access_list:
                self.validate_firewall(firewall)

            clouds = settings.clouds
            if clouds[0]['name'] in ['', None]:
                utils.error(f'Invalid cloud name, Please edit the settings file correctly')
                return
            label = f'All available clouds in the settings file are:'
            utils.colour_print(
                '┌─────────────────────────────────────────────────┐',
            )
            utils.colour_print(f'│{label:^49}│')
            utils.colour_print(
                '├───────────┬─────────────────────────────────────┤',
            )
            utils.colour_print(
                '│     id    │                 Name                │',
            )
            utils.colour_print(
                '├───────────┼─────────────────────────────────────┤',
            )
            cloud_ids = []
            for cloud in clouds:
                cloud_ids.append(cloud['id'])
                utils.colour_print(f'│{cloud["id"]:^11}│{cloud["name"]:^37}│')
            utils.colour_print(
                '└───────────┴─────────────────────────────────────┘',
            )
            cloud_id = input(
                utils.colour('(colour_warning)Select the cloud by entering "id" of the cloud.(colour_clear): '),
            )
            if cloud_id not in cloud_ids:
                utils.error('Invalid cloud id, exiting. Please try again with correct cloud id.')
                return
            the_cloud = None
            for cloud in clouds:
                if cloud['id'] == cloud_id:
                    the_cloud = cloud
            # validating the cloud settings
            utils.colour_print('Validating COP_ACCESS_LIST ...')
            cop_access_list = the_cloud['COP_ACCESS_LIST']
            for firewall in cop_access_list:
                self.validate_firewall(firewall)

            pods = the_cloud['pods']
            label = f'All available pods from the cloud #{the_cloud["name"]} are:'
            utils.colour_print(
                '┌───────────────────────────────────────────────────────────┐',
            )
            utils.colour_print(f'│{label:^59}│')
            utils.colour_print(
                '├───────────┬────────────────────────────────────┬──────────┤',
            )
            utils.colour_print(
                '│     id    │                 Name               │   Type   │',
            )
            utils.colour_print(
                '├───────────┼────────────────────────────────────┼──────────┤',
            )
            pod_ids = []
            for pod in pods:
                pod_ids.append(pod['id'])
                utils.colour_print(f'│{pod["id"]:^11}│{pod["name"]:^36}│{pod["type"]:^10}│')
            utils.colour_print(
                '└───────────┴────────────────────────────────────┴──────────┘',
            )
            pod_id = input(
                utils.colour('(colour_warning)Select the pod by entering "id" of the pod.(colour_clear):  '),
            )
            if pod_id not in pod_ids:
                utils.error('Invalid pod id, exiting. Please try again with correct pod id.')
                return
            the_pod = None
            for pod in pods:
                if pod['id'] == pod_id:
                    the_pod = pod

            public_port_config = []
            # validating the pod settings
            utils.colour_print('validating IPv4_link_subnet...')
            for subnet in the_pod['IPv4_link_subnet']:
                if subnet['address_range'] != '':
                    if not self.validate_address(subnet['address_range']):
                        utils.error(f'Invalid address_range in IPv4_link_subnet #{subnet}')
                        exit()
                    if not self.validate_address(subnet['gateway']):
                        utils.error(f'Invalid gateway in IPv4_link_subnet #{subnet}')
                        exit()
                    public_port_config.append(subnet)

            utils.colour_print('validating IPv4_pod_subnets...')
            for subnet in the_pod['IPv4_pod_subnets']:
                if not self.validate_address(subnet['address_range']):
                    utils.error(f'Invalid address_range in IPv4_pod_subnets #{subnet}')
                    exit()
                if not self.validate_address(subnet['gateway']):
                    utils.error(f'Invalid gateway in IPv4_link_subnet #{subnet}')
                    exit()
                public_port_config.append(subnet)

            utils.colour_print('validating IPv6_link_subnet...')
            for subnet in the_pod['IPv6_link_subnet']:
                if not self.validate_address(subnet['address_range']):
                    utils.error(f'Invalid address_range in IPv6_link_subnet #{subnet}')
                    exit()
                if not self.validate_address(subnet['gateway']):
                    utils.error(f'Invalid gateway in IPv6_link_subnet #{subnet}')
                    exit()
                public_port_config.append(subnet)

            mgmt_port_config = []
            utils.colour_print('validating IPv6_pod_subnets...')
            for subnet in the_pod['IPv6_pod_subnets']:
                if not self.validate_address(subnet['address_range']):
                    utils.error(f'Invalid address_range in IPv6_pod_subnets #{subnet}')
                    exit()
                address = subnet['address_range'].split('/')
                subnet['address_range'] = f'{address[0]}10:0:1/64'
                subnet['gateway'] = f'{address[0]}10:0:1'
                mgmt_port_config.append(subnet)

            utils.colour_print('validating IPv4_RFC1918_subnets...')
            for subnet in the_pod['IPv4_RFC1918_subnets']:
                if not self.validate_address(subnet['address_range']):
                    utils.error(f'Invalid address_range in IPv4_RFC1918_subnets #{subnet}')
                    exit()
                if not self.validate_address(subnet['gateway']):
                    utils.error(f'Invalid gateway in IPv4_RFC1918_subnets #{subnet}')
                    exit()
                mgmt_port_config.append(subnet)

            access_addrs = map_access_list + cop_access_list
            mgmt_access_addresses = []
            for item in access_addrs:
                # an address is defined with name in router, the name can be any unique so is taken from ip address
                # itself by converting its non integers like '.' , '/', ':' to '-'.
                item['source_address_name'] = ADDRESS_NAME_SUB_PATTERN.sub('-', item['source_address'])
                item['destination_address_name'] = ADDRESS_NAME_SUB_PATTERN.sub('-', item['destination_address'])
                mgmt_access_addresses.append(item)

            template_data: Optional[Dict[str, Any]]
            template_data = {
                'name_servers': settings.ROUTER_NAME_SERVERS,
                'mgmt_access_addresses': mgmt_access_addresses,
                'robot_rsa': settings.ROBOT_RSA,
                'rocky_rsa': settings.ROCKY_RSA,
                'administrator_encryp_pass': settings.ADMINISTRATOR_ENCRYP_PASS,
                'api_user': settings.API_USER_PASS,
                'radius_server_address': settings.RADIUS_SERVER_ADDRESS,
                'radius_server_secret': settings.RADIUS_SERVER_SECRET,
                'location': the_pod['location'],
                'name': the_pod['name'],
            }
            utils.line_break()
            print()

            # Get the oob router
            utils.colour_print('(colour_prompt)Please enter correct OOB ip of the router to be scrubbed(colour_clear).')
            utils.colour_print('\r - e.g 10.S.R.U where S:site number; R:rack number; U:unit location')
            utils.colour_print('\r - each must be in range 0-254')
            oob_ip = self.user_input_valid_address('')
            utils.line_break()
            print()

            # SSHing into router for router model
            utils.colour_print('(colour_prompt)Fetching the router model...(colour_clear)')
            router_model = RouterScrub.router_model(oob_ip)
            if not router_model:
                utils.error(f'Failed to fetch router model for given ip #{oob_ip}, Check the oob ip and try again.')
                return
            utils.colour_print(
                f'The router model for given ip #{oob_ip} is (colour_success){router_model}(colour_clear)',
            )
            utils.line_break()
            print()

            # oob 10.S.R.U S:site; R:rack; U:unit
            template_data['router'] = {
                'router_ip': oob_ip,
                'router_location': oob_ip.replace('.', ''),  # 10SRU
                'router_model': router_model,
            }

            # sshing into router for root encrypted password
            utils.colour_print('(colour_prompt)Fetching the root encrypted password...(colour_clear)')
            root_encrypt_password = RouterScrub.root_encrypted_password(oob_ip)
            if not root_encrypt_password:
                utils.error(f'Failed to fetch root encrypted password from router.')
                return
            utils.colour_print(
                f'Found root encrypted password of router #{oob_ip}',
            )
            template_data['root_encrypted_password'] = root_encrypt_password
            utils.line_break()
            print()

            # confirm if router model is fibre or copper in case SRX345-DUAL-AC
            if router_model in ['SRX345-DUAL-AC', 'SRX345']:
                router_model = 'SRX345'
                utils.colour_print('(colour_prompt)Type of router cabling: ')
                utils.colour_print('(colour_prompt)\r - 1. Copper')
                utils.colour_print('(colour_prompt)\r - 2. Fibre')
                option = ''
                while option not in ['1', '2']:
                    option = utils.user_input_validate(
                        utils.colour('(colour_warning)Please enter "1" for Copper or "2" for Fibre.(colour_clear)'),
                    )
                    if str(option) == '1':
                        router_model = f'{router_model}-Copper'
                        utils.colour_print(f'(colour_prompt)Preparing router scrub for {router_model}...(colour_clear)')
                    if str(option) == '2':
                        router_model = f'{router_model}-Fibre'
                        utils.colour_print(f'(colour_prompt)Preparing router scrub for {router_model}...(colour_clear)')
            else:
                utils.colour_print(f'(colour_prompt)Preparing router scrub for {router_model}...(colour_clear)')
            utils.line_break()
            print()

            # Prepare the router's specs from json.
            try:
                with open('data/router_specs.json', 'r') as f:
                    template_data['ports'] = json.load(f)['routers'][f'{router_model}']
            except:
                utils.error('An error occurred while preparing router scrub')
                traceback.print_exc()
                return

            # Collect the template data.
            for port in template_data['ports']:

                # oob is already taken
                if port['function'] == 'OOB':
                    port['port_configs'].append(
                        {
                            'ip': oob_ip,
                            'mask': 16,  # /16 for oob is by design, if changes should reflect here.
                            'type': 'inet',
                            'gateway': f'10.{oob_ip.split(".")[1]}.0.1',
                        },
                    )

                # Management
                if port['function'] == 'Management':
                    for address in mgmt_port_config:
                        ip = address['address_range'].split('/')
                        port['port_configs'].append(
                            {
                                'ip': ip[0],
                                'mask': ip[1],
                                'type': 'inet6' if netaddr.IPAddress(ip[0]).version == 6 else 'inet',
                                'gateway': address['gateway'],
                            },
                        )

                # Public
                if port['function'] == 'Floating':
                    for address in public_port_config:
                        ip = address['address_range'].split('/')
                        port['port_configs'].append(
                            {
                                'ip': ip[0],
                                'mask': ip[1],
                                'type': 'inet6' if netaddr.IPAddress(ip[0]).version == 6 else 'inet',
                                'gateway': address['gateway'],
                            },
                        )

            # All data check
            label = f'Router #{router_model} {oob_ip} ports and IPs'
            utils.colour_print(
                '┌─────────────────────────────────────────────────────────────────────────────────────────┐',
            )
            utils.colour_print(f'│{label:^89}│')
            utils.colour_print(
                '├───────────┬─────────────┬───────────────────────────┬───────┬───────────────────────────┤',
            )
            utils.colour_print(
                '│   Name    │  Function   │            IPs            │  Mask │         Gateway           │',
            )
            utils.colour_print(
                '├───────────┼─────────────┼───────────────────────────┼───────┼───────────────────────────┤',
            )

            for port in template_data['ports']:
                function = port['function']
                name = port['name']
                if function != 'Private':

                    port_configs = port['port_configs']
                    for i, ip in enumerate(port_configs):

                        # proper print
                        if i == 0:
                            utils.colour_print(
                                f'│{name:^11}│{function:^13}│{ip["ip"]:^27}│{ip["mask"]:^7}│{ip["gateway"]:^27}│',
                            )
                        else:
                            utils.colour_print(
                                f'│{"":^11}│{"":^13}│{ip["ip"]:^27}│{ip["mask"]:^7}│{ip["gateway"]:^27}│',
                            )
                else:
                    utils.colour_print(
                        f'│{name:^11}│{function:^13}│{"-":^27}│{"-":^7}│{"-":^27}│',
                    )

            utils.colour_print(
                '└───────────┴─────────────┴───────────────────────────┴───────┴───────────────────────────┘')
            utils.line_break()

            yes = input(
                utils.colour('If you want to continue press Y or y, else press any key to stop.: '),
            )
            utils.line_break()
            print()
            if yes in ['Y', 'y']:
                RouterScrub.scrub(template_data)

        except:
            utils.error('An error occurred while configuring ports on router')
            traceback.print_exc()

    @staticmethod
    def validate_address(address):
        """
        validates the given address or address range
        """
        try:
            if netaddr.IPNetwork(address):
                return True
        except:
            address = address
            utils.colour_print(f'(colour_warning) {address} is not a valid IP address.(colour_clear)')
            return False

    @classmethod
    def user_input_valid_address(cls, print_statement: str):

        """
        takes user input and verifies and return valid address.
        """
        address = ''
        while address == '':

            address = utils.user_input_validate(print_statement)
            if address:
                if cls.validate_address(address):
                    break
            address = ''

        return address

    @classmethod
    def validate_firewall(cls, firewall):
        """
        takes a firewall rule dict with source address, destination address, port and protocol
        :param firewall:
        :return: nothing if everything is right otherwise fails gracefully
        """
        if 'source_address' not in firewall.keys():
            utils.error(f'"source_address" is not defined for firewall # {firewall}')
            exit()
        if firewall['source_address'] == 'any':
            pass
        elif not cls.validate_address(firewall['source_address']):
            utils.error(f'Invalid "source_address" for firewall # {firewall}')
            exit()
        if 'destination_address' not in firewall.keys():
            utils.error(f'"destination_address" is not defined for firewall # {firewall}')
            exit()
        if firewall['destination_address'] == 'any':
            pass
        elif not cls.validate_address(firewall['destination_address']):
            utils.error(f'Invalid "destination_address" for firewall # {firewall}')
            exit()
        if 'port' not in firewall.keys():
            utils.error(f'"port" is not defined for firewall #{firewall}')
            exit()
        if firewall['port'] == 'any':
            pass
        else:
            ports = firewall['port'].split('-')
            for port in ports:
                if int(port) not in range(65536):
                    utils.error(f'Invalid port value # {port} of firewall #{firewall}, it must be in range 0 to 65536')
                    exit()
        if 'protocol' not in firewall.keys():
            utils.error(f'"protocol" is not defined for firewall #{firewall}')
            exit()
        if firewall['protocol'] not in ['tcp', 'upd', 'any']:
            utils.error(f'Invalid protocol for firewall #{firewall}, it can only be "tcp" or "udp", or "any".')
            exit()
