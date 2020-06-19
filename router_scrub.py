# stdlib
import json
import re
import traceback
from typing import Any, Dict, Optional
# libs
import netaddr
# local
from bin import RouterMixin, utils
import rocky

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
            '\u2502' + (' ' * 2) + '(colour_clear)will cause service outages'
            '(colour_cmd)' + (' ' * 2) + '\u2502')
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

            # Management network is controlled by SRX routers and are firewall protected, so all inbound is blocked.
            # An allow policy with the access list ips can enable the access to management network from outside world.
            # Access list can be api servers, gitlab servers and etc, where the management hosts like Robot needs to
            # communicate with these servers in access list.
            access_addrs = rocky.SETTINGS['MGMT_ACCESS_LIST']
            mgmt_access_addresses = []
            for key in access_addrs:
                # an address is defined with name in router, the name can be any unique so is taken from ip address
                # itself by converting its non integers like '.' , '/', ':' to '-'.
                key_pattern = ADDRESS_NAME_SUB_PATTERN.sub('-', access_addrs[key])
                mgmt_access_addresses.append([access_addrs[key], key, key_pattern])

            template_data: Optional[Dict[str, Any]]
            template_data = {
                'name_servers': rocky.SETTINGS['ROUTER_NAME_SERVERS'],
                'mgmt_access_addresses': mgmt_access_addresses,
                'robot_rsa': rocky.SETTINGS['ROBOT_RSA'],
                'rocky_rsa': rocky.SETTINGS['ROCKY_RSA'],
            }

            # Get the oob router
            utils.colour_print('(colour_prompt)Please enter correct OOB ip of the router to be scrubbed(colour_clear).')
            utils.colour_print('\r - e.g 10.S.R.U where S:site number; R:rack number; U:unit location')
            utils.colour_print('\r - each must be in range 1-254')
            oob_ip = self.user_input_valid_address('')
            utils.line_break()
            print()

            # sshing into router for router model
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
            utils.colour_print('(colour_prompt)Please enter requested information correctly(colour_clear).\n')
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

                    utils.colour_print('(colour_prompt)MANAGEMENT port configuration(colour_clear).\n')
                    utils.colour_print(
                        '(colour_prompt)Please give /48 (e.g "2a02:2078:3::/48") address range:(colour_clear)',
                    )
                    management = self.user_input_valid_address('')
                    ip = f'{management.split("/")[0]}10:0:1'
                    port['port_configs'].append(
                        {
                            'ip': ip,
                            'mask': 64,
                            'type': 'inet6',
                            'gateway': ip,
                        },
                    )
                    # Management private network 172.16.10.0/24
                    port['port_configs'].append(
                        {
                            'ip': '172.16.10.1',
                            'mask': 24,
                            'type': 'inet',
                            'gateway': '172.16.10.1',
                        },
                    )
                    utils.line_break()
                    print()

                # Public
                if port['function'] == 'Floating':

                    utils.colour_print('(colour_prompt)PUBLIC port configuration(colour_clear).\n')
                    utils.colour_print('Please give a valid floating address range:(colour_clear)')
                    utils.colour_print('- e.g "91.103.0.62/27"; "2a02:2078::148/126"(colour_clear)')
                    more = True
                    while more:

                        floating = self.user_input_valid_address('Floating: ')
                        gateway = self.user_input_valid_address('Gateway: ')

                        if str(gateway) in netaddr.IPNetwork(floating):

                            ip = floating.split('/')
                            port['port_configs'].append(
                                {
                                    'ip': ip[0],
                                    'mask': ip[1],
                                    'type': 'inet6' if netaddr.IPAddress(ip[0]).version == 6 else 'inet',
                                    'gateway': gateway,
                                },
                            )

                            option = input(
                                utils.colour(
                                    '(colour_prompt)If you want to add address range, '
                                    'enter y or Y otherwise any key to stop.:(colour_clear) ',
                                ),
                            )
                            if option not in ['Y', 'y']:
                                break
                        else:
                            utils.colour_print(
                                f'(colour_warning)This {gateway} is not a valid gateway'
                                f' of {floating}, try again.(colour_clear)',
                            )
                    utils.line_break()
                    print()

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
