# stdlib
import json
import traceback
# libs
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


class Checker(Hosts):

    def __init__(self):
        Hosts.__init__(self)
        self.pass_count_total = 0
        self.fail_count_total = 0
        self.added_count_total = 0
        self.removed_count_total = 0

    def _port_print(self, port: dict):  # Port Printing
        if len(port) == 3:
            colour_print(
                f'name:{port["name"]}  '
                f'oper-status:{port["oper-status"]}  '
                f'admin-status:{port["admin-status"]}  ')
        else:
            colour_print(
                f'name:{port["name"]}  '
                f'oper-status:{port["oper-status"]}  '
                f'admin-status:{port["admin-status"]}  '
                f'description:{port["description"]}  ')
        return

    def _summary_print(self, pass_count: int, fail_count: int, add_count: int, remove_count: int):
        colour_print(f'(colour_prompt) Pass Count = {pass_count} (colour_cmd)')
        colour_print(f'(colour_warning) Fail Count = {fail_count} (colour_cmd)')
        colour_print(f'(colour_warning) Added Count = {add_count} (colour_cmd)')
        colour_print(f' Removed Count = {remove_count} (colour_cmd)')
        line_break()

    def checker(self, password: str):

        for host in self.rocky_hosts:

            line_break()
            colour_print(
                f'(colour_cmd){host["host_name"]} {host["ip"]} {host["username"]} ',
            )

            line_break()

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

                convert_to_string = etree.tostring(interfaces)

                parsed_dict = dict(xmltodict.parse(convert_to_string))
                # Strip out only 'interface-information'
                parsed_dict = parsed_dict['interface-information']
                # Strip out only 'physical-interface'
                scanned_device = parsed_dict['physical-interface']

                for port in scanned_device:
                    # If logical interfaces, delete them.
                    try:

                        del port['logical-interface']

                    except KeyError:
                        pass
                # Get the Learned device data
                try:
                    # if a new device is added but its learned json file from
                    # ports dir is missing so it throws error
                    learned_device = []

                    filename = f'data_hosts/ports/{host["host_name"]}.json'

                    with open(filename, 'r') as port_json:

                        for line in port_json:
                            learned_device.append(json.loads(line))

                    # Comparison starts
                    pass_count = 0
                    fail_count = 0
                    added_count = 0
                    removed_count = 0
                    # Loop for Port finding

                    for scanned_port in scanned_device:

                        port_check = 'notfound'

                        for learned_port in learned_device:

                            if scanned_port['name'] == learned_port['name']:  # Port matching

                                port_check = 'found'
                                # Port properties matching
                                oper_status = (
                                    scanned_port['oper-status'] == learned_port['oper-status'],
                                )

                                admin_status = (
                                    scanned_port['admin-status'] == learned_port['admin-status'],
                                )

                                if oper_status and admin_status:

                                    pass_count += 1
                                    self.pass_count_total += 1

                                else:

                                    fail_count += 1
                                    self.fail_count_total += 1

                                    # TODO: come back to this
                                    colour_print('(colour_clear)Learned:-> (colour_success)')
                                    self._port_print(learned_port)
                                    colour_print('(colour_clear)Scanned:-> (colour_warning)')
                                    self._port_print(learned_port)
                                break

                        if port_check == 'found':

                            # deleting found ports, then left over ports are
                            # removed ports
                            learned_device.remove(learned_port)

                        else:

                            added_count += 1
                            self.added_count_total += 1

                            colour_print('(colour_prompt)ADDED:->')
                            self._port_print(scanned_port)

                    if len(learned_device) != 0:

                        for removed_port in learned_device:

                            removed_count += 1
                            self.removed_count_total += 1

                            colour_print('(colour_warning)REMOVED:->')
                            colour_print(f'{self._port_print(removed_port)}(colour_cmd)\n')

                    self._summary_print(
                        pass_count,
                        fail_count,
                        added_count,
                        removed_count,
                    )

                except Exception:  # NOQA
                    # New device found, so displays it's ports configuration
                    colour_print('(colour_warning)Newly Added Device and it\'s ports are: ')
                    colour_print('(colour_cmd)')

                    for new_port in scanned_device:

                        self._port_print(new_port)
                        self.added_count_total += 1

                    line_break()

            except:
                error(f'Unable to connect to the Host')
                traceback.print_exc()
                line_break()

        print(f'SUMMARY: {len(self.rocky_hosts)} DEVICE(S) SCANNED\nTotal: ')

        self._summary_print(
            self.pass_count_total,
            self.fail_count_total,
            self.added_count_total,
            self.removed_count_total,
        )

        # loop around devices
        for host in self.juniper_hosts:

            print(
                host['host_name'],
                host['ip'],
                host['username'],
            )

            line_break()
            # call devices
            dev = Device(
                host=host['ip'],
                user=host['username'],
                password=password,
                port=22,
            )

            try:   # in case device goes down it throws error
                dev.open()

                interfaces = dev.rpc.get_interface_information(
                    terse=True,
                )

                dev.close()
                convert_to_string = etree.tostring(interfaces)
                parsed_dict = dict(xmltodict.parse(convert_to_string))
                # Strip out only 'interface-information'
                parsed_dict = parsed_dict['interface-information']
                # Strip out only 'physical-interface'
                scanned_device = parsed_dict['physical-interface']

                for port in scanned_device:  # list of dictionaries
                    # If logical interfaces, delete them.
                    try:
                        del port['logical-interface']
                    except KeyError:
                        pass
                # Get the Learned device data

                try:
                    #  if a new device is added but its learned json file from
                    # ports dir is missing so it throws error
                    learned_device = []
                    filename = f'data_hosts/ports/{host["host_name"]}.json'

                    with open(filename, 'r') as port_json:

                        for line in port_json:

                            learned_device.append(json.loads(line))

                    # Comparison starts
                    fail_count = 0
                    pass_count = 0
                    added_count = 0
                    removed_count = 0

                    # Loop for Port finding
                    for scanned_port in scanned_device:

                        port_check = 'notfound'

                        for learned_port in learned_device:

                            if scanned_port['name'] == learned_port['name']:  # Port matching

                                port_check = 'found'

                                # Port properties matching
                                oper_status = (
                                    scanned_port['oper-status'] == learned_port['oper-status']
                                )

                                admin_status = (
                                    scanned_port['admin-status'] == learned_port[
                                        'admin-status']
                                )

                                if oper_status and admin_status:

                                    pass_count += 1
                                    self.pass_count_total += 1

                                else:

                                    fail_count += 1
                                    self.fail_count_total += 1

                                    colour_print('(colour_prompt)Learned:-> ')
                                    self._port_print(learned_port)
                                    colour_print('(colour_warning)Scanned:-> ')
                                    self._port_print(scanned_port)

                                break

                        if port_check == 'found':
                            # deleting found ports, then left over ports are
                            # removed ports
                            learned_device.remove(learned_port)

                        else:

                            added_count += 1
                            self.added_count_total += 1

                            colour_print('(colour_prompt)ADDED:->')
                            self._port_print(scanned_port)

                    if len(learned_device) != 0:

                        for removed_port in learned_device:

                            removed_count += 1
                            self.removed_count_total += 1

                            colour_print('(colour_warning)REMOVED:->')
                            self._port_print(removed_port)

                    self._summary_print(
                        pass_count,
                        fail_count,
                        added_count,
                        removed_count,
                    )

                except Exception:  # NOQA
                    # New device found, so displays it's ports configuration
                    colour_print('(colour_warning)Newly Added Device and it\'s ports are: ')
                    colour_print('(colour_cmd)')

                    for new_port in scanned_device:

                        {self._port_print(new_port)}
                        self.added_count_total += 1

                    line_break()

            except:
                colour_print(f'(colour_warning)Unable to connect to Host(colour_cmd)')
                traceback.print_exc()
                line_break()

        print(f'SUMMARY: {len(self.juniper_hosts)} DEVICE(S) SCANNED\nTotal:')

        self._summary_print(
            self.pass_count_total,
            self.fail_count_total,
            self.added_count_total,
            self.removed_count_total,
        )

    def run(self, password: str):
        self.checker(password)
