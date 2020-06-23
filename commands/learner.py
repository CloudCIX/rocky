# stdlib
import json
# lib
from jnpr.junos import Device
from lxml import etree
import xmltodict
# local
from bin import Hosts
from bin.utils import (
    colour_print,
    error,
    line_break,
)
import settings


class Learner(Hosts):
    """
    Command: learner

    Desc: inherits hosts from Hosts and learns about its information
    """
    def __init__(self):
        Hosts.__init__(self)

    def learner(self, password: str):

        self.prompt()
        confirm = input(' ').lower()

        if confirm != 'y':
            return None

        line_break()

        for host in self.juniper_hosts:

            print(
                host['host_name'],
                host['ip'],
                host['username'],
            )

            dev = Device(
                host=host['ip'],
                user=host['username'],
                password=password,
                port=22,
            )

            try:
                dev.open()

                interfaces = dev.rpc.get_interface_information(
                    terse=True,
                )

                dev.close()

                interfaces = etree.tostring(interfaces)
                parsed_dict = dict(xmltodict.parse(interfaces))

                parsed_dict = parsed_dict['interface-information']
                parsed_list = parsed_dict['physical-interface']

                with open(f'{settings.PORTS_PATH}{host["host_name"]}.json', 'w+') as file:

                    for item in parsed_list:

                        try:

                            del item['logical-interface']

                        except KeyError:
                            pass

                        file.write(f'{json.dumps(item)}\n')

                print(f'{settings.PORTS_PATH}{host["host_name"]}.json saved')
                line_break()

            except Exception as err:
                error(f'Unable to find the Host {err}')
                line_break()

        line_break()

        for host in self.rocky_hosts:

            print(
                host['host_name'],
                host['ip'],
                host['username'],
            )

            # call devices
            dev = Device(
                host=host['ip'],
                user=host['username'],
                password=password,
                port=22,
            )

            try:
                dev.open()

                interfaces = dev.rpc.get_interface_information(
                    terse=True,
                )

                dev.close()

                interfaces = etree.tostring(interfaces)
                parsed_dict = dict(xmltodict.parse(interfaces))
                # Strip out only 'interface-information'
                parsed_dict = parsed_dict['interface-information']
                # Strip out only 'physical-interface'
                parsed_list = parsed_dict['physical-interface']
                # Storing port properties

                with open(f'{settings.PORTS_PATH}{host["host_name"]}.json', 'w+') as file:

                    for item in parsed_list:
                        # If logical interfaces, delete them.
                        try:
                            del item['logical-interface']

                        except KeyError:
                            pass
                        # format for storing each port-configuration falls in
                        # each column
                        file.write(f'{json.dumps(item)}\n')

                print(f'{settings.PORTS_PATH}{host["host_name"]}.json saved')
                line_break()

            except Exception as err:
                print(f'Unable to find Host {err}')
                line_break()

    def run(self, password: str):
        self.learner(password)

    def prompt(self):
        print()
        colour_print('(colour_cmd)\u250D' + ('\u2501' * 50) + '\u2511')
        colour_print('\u2502' + (' ' * 50) + '\u2502')
        colour_print(
            '\u2502' + (' ' * 21) + '(colour_warning)WARNING:(colour_cmd)' + (' ' * 21) + '\u2502')
        colour_print(
            '\u2502' + (' ' * 8) + '(colour_clear)Do not run Port Learner '
            'until you(colour_cmd)' + (' ' * 9) + '\u2502')
        colour_print(
            '\u2502' + (' ' * 8) + '(colour_clear)have run Port Checker and '
            'you have(colour_cmd)' + (' ' * 8) + '\u2502')
        colour_print(
            '\u2502' + (' ' * 12) + '(colour_clear)verified any changed '
            'ports.(colour_cmd)' + (' ' * 11) + '\u2502')
        colour_print(
            '\u2502' + (' ' * 50) + '\u2502')
        colour_print(
            '\u2502' + (' ' * 6) + '(colour_clear)Once the new port statuses are '
            'learned(colour_cmd)' + (' ' * 6) + '\u2502')
        colour_print(
            '\u2502' + (' ' * 8) + '(colour_clear)the new values will be the '
            'norm and(colour_cmd)' + (' ' * 7) + '\u2502')
        colour_print(
            '\u2502' + (' ' * 13) + '(colour_clear)problems may be '
            'masked.(colour_cmd)' + (' ' * 14) + '\u2502')
        colour_print(
            '\u2502' + (' ' * 50) + '\u2502')
        colour_print(
            '\u2502' + (' ' * 8) + '(colour_clear)Press (colour_cmd)y (colour_clear)to continue'
            ' or press (colour_cmd)ENTER(colour_cmd)' + (' ' * 8) + '\u2502')
        colour_print(
            '\u2502' + (' ' * 12) + '(colour_clear)to return to the (colour_rocky)Rocky '
            '(colour_clear)CLI.(colour_cmd)' + (' ' * 11) + '\u2502')
        colour_print(
            '\u2502' + (' ' * 50) + '\u2502')
        colour_print(
            '\u2515' + ('\u2501' * 50) + '\u2519(colour_clear)')
        print()
