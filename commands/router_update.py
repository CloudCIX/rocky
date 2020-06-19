# stdlib
import os
import re
import traceback
from typing import Any, Dict, Optional
# local
from bin import cloud, RouterMixin, utils
import rocky

ADDRESS_NAME_SUB_PATTERN = re.compile(r'[\.\/:]')


class RouterUpdate(RouterMixin):

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
            '(colour_clear)to continue.(colour_cmd)' + (' ' * 4) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 5) + '(colour_clear)Press (colour_cmd)RETURN '
            '(colour_clear)to exit.(colour_cmd)' + (' ' * 4) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 30) + '\u2502')
        utils.colour_print(
            '\u2515' + ('\u2501' * 30) + '\u2519(colour_clear)')
        print()

    def run_router(self):
        try:
            os.environ.setdefault('CLOUDCIX_SETTINGS_MODULE', 'settings')
            from cloudcix import api
            from cloudcix.auth import get_admin_token
            self.prompt()

            if input() not in ['Y', 'y']:
                return

            access_addrs = rocky.SETTINGS['MGMT_ACCESS_LIST']
            mgmt_access_addresses = []
            for key in access_addrs:
                key_pattern = ADDRESS_NAME_SUB_PATTERN.sub('-', access_addrs[key])
                mgmt_access_addresses.append([access_addrs[key], key, key_pattern])

            set_data: Optional[Dict[str, Any]]
            set_data = {
                'name_servers': rocky.SETTINGS['ROUTER_NAME_SERVERS'],
                'mgmt_access_addresses': mgmt_access_addresses,
            }

            addresses = cloud.service_entity_list('Membership', 'address', {'search[member_id]': '2'})
            # Display the regions
            valid_ids = set()
            print()
            utils.colour_print('┌────────────────────────────────────────────────────────────────┐')
            utils.colour_print('│                 All regions under idMember = 2                 │')
            utils.colour_print('├────────┬───────────────────────────────────────────────────────┤')
            utils.colour_print('│   ID   │              Name              │         City         │')
            utils.colour_print('├────────┼───────────────────────────────────────────────────────┤')
            for address in addresses:
                utils.colour_print(f'│{address["id"]:^8}│{address["name"]:^32}│{address["city"]:^22}│')
                valid_ids.add(str(address['id']))
            utils.colour_print('└────────┴────────────────────────────────┴──────────────────────┘')
            # choose a region
            utils.colour_print('Please choose a region ID from the (colour_cmd)ID (colour_clear)list above: ')
            try:
                region = int(input(''))
            except TypeError:
                utils.error('Incorrect region ID format')
                return

            router_region = [address['name'] for address in addresses if address['idAddress'] == region]
            if len(router_region) == 0:
                utils.colour_print('(colour_warning)Chosen incorrect region ID, exiting, retry carefully.')
                return

            routers = cloud.service_entity_list('IAAS', 'router', {'region': region})
            if len(routers) == 0:
                utils.colour_print(f'(colour_warning)No Routers found in region #{region}, exiting.')
                return
            region_name = router_region[0]
            utils.line_break()
            print()

            # Get router's data
            router_ids = []
            router_rmpf = {}
            rmpf_ids = []
            asset_ids = []
            for router in routers:
                router_ids.append(router['idRouter'])
                ports = cloud.service_entity_list('IAAS', 'port', {}, router_id=router['idRouter'])
                rmpf_ids.append(ports[0]['model_port_id'])
                router_rmpf[router['idRouter']] = ports[0]['model_port_id']
                asset_ids.append(router['idAsset'])

            # Get the Router Model Port Function instances
            rmpf_params = {'model_port_id__in': rmpf_ids}
            rmpfs = cloud.service_entity_list('IAAS', 'router_model_port_function', params=rmpf_params)

            # Get the Router Models
            rmpf_model = {}
            for rmpf in rmpfs:
                rmpf_model[rmpf['model_port_id']] = rmpf['router_model_id']
            router_model_ids = [rmpf['router_model_id'] for rmpf in rmpfs]
            model_params = {'router_model_id__in': router_model_ids}
            router_models = cloud.service_entity_list('IAAS', 'router_model', params=model_params)

            # model <-> model data
            model_data = {}
            for router_model in router_models:
                model_data[router_model['router_model_id']] = [router_model['model'], router_model['vrMax']]
            # router's location and oob ip as {'asset_id': [location, oob_ip]}
            assets_params = {'id__in': asset_ids}
            assets = cloud.service_entity_list('Asset', 'asset', params=assets_params)
            assets_data = {}
            for asset in assets:
                location = asset['location']
                asset_details = cloud.get_idrac_details(location)
                assets_data[asset['id']] = [location, asset_details['ip']]

            # Print the details
            label = f'Routers in region #{region}'
            utils.colour_print('┌──────────────────────────────────────────────────────────┐')
            utils.colour_print(f'│{label:^58}│')
            utils.colour_print('├────────┬─────────────────────┬──────────┬────────────────┤')
            utils.colour_print('│   ID   │        Model        │ Capacity │    Location    │')
            utils.colour_print('├────────┼─────────────────────┼──────────┼────────────────┤')
            for router in routers:
                # final: router <-> model data
                model, vr_max = model_data[rmpf_model[router_rmpf[router['idRouter']]]]
                location = assets_data[router['idAsset']][0]
                utils.colour_print(f'│{router["idRouter"]:^8}│{model:^21}│{vr_max:^10}│{location:^16}│')
            utils.colour_print('└────────┴─────────────────────┴──────────┴────────────────┘')
            print()
            # choose a router
            utils.colour_print('Please choose a router ID from the (colour_cmd)Router (colour_clear)list above: ')
            try:
                router_id = int(input())
            except TypeError:
                utils.error('Invalid Router ID.')
                return
            if router_id not in router_ids:
                utils.error('Chosen incorrect option, exiting. Retry carefully.')
                return
            utils.line_break()
            print()

            # asset data of this router
            asset_id = [router['idAsset'] for router in routers if router['idRouter'] == router_id][0]
            router_oob_ip = assets_data[asset_id][1]

            # router data for set config template
            set_data['router'] = {
                'router_id': router_id,
                'router_model': model_data[rmpf_model[router_rmpf[router_id]]][0],
                'region_name': region_name,
            }

            # PORTS data
            set_data['ports'] = []

            router_ports = cloud.service_entity_list('IAAS', 'port', {}, router_id=router_id)
            if not router_ports:
                utils.error(f'Router #{router_id} has no ports defined in database')
                return

            # Get the rmpfs of ports
            router_rmpf_ids = [router_port['model_port_id'] for router_port in router_ports]
            rmpfs_params = {'model_port_id__in': router_rmpf_ids}
            router_rmpfs = cloud.service_entity_list('IAAS', 'router_model_port_function', params=rmpfs_params)

            # Get the Port function instances
            pf_ids = [router_rmpf['port_function_id'] for router_rmpf in router_rmpfs]
            pf_params = {'port_function_id__in': pf_ids}
            port_functions = cloud.service_entity_list('IAAS', 'port_function', params=pf_params)

            # port_id <-> [port name, port_function]
            port_rmpf_pfs = {}  # type: dict
            for port in router_ports:
                for router_rmpf in router_rmpfs:
                    for port_function in port_functions:
                        if port['model_port_id'] == router_rmpf['model_port_id'] and \
                                router_rmpf['port_function_id'] == port_function['port_function_id']:
                            port_rmpf_pfs[port['port_id']] = [router_rmpf['port_name'], port_function['function']]
                            break

            # Port <-> IPAddresses
            port_configs = []
            for port in router_ports:
                port_configs.extend(cloud.service_entity_list('IAAS', 'port_config', {}, port_id=port['port_id']))
            port_config_ip_ids = [port_config['port_ip_id'] for port_config in port_configs]
            port_config_ip_params = {'idIPAddress__in': port_config_ip_ids}
            port_config_ips = cloud.service_entity_list('IAAS', 'ipaddress', params=port_config_ip_params)

            # Get the nature of ip addresses
            addresses = [port_config_ip['address'] for port_config_ip in port_config_ips]
            ip_addresses = ','.join(address for address in addresses)
            result = api.IAAS.ip_validator.list(token=get_admin_token(), params={'ipAddresses': ip_addresses}).json()

            ip_subnet_ids = [port_config_ip['idSubnet'] for port_config_ip in port_config_ips]
            subnets = cloud.service_entity_list('IAAS', 'subnet', params={'idSubnet__in': ip_subnet_ids})

            ips_data = {}  # ips <-> ips_data relation
            for port_config_ip in port_config_ips:
                address = port_config_ip['address']
                ip_type = 'inet'
                if result['ipAddresses'][address]['result']['ipv6']:
                    ip_type = 'inet6'
                for subnet in subnets:
                    if port_config_ip['idSubnet'] == subnet['idSubnet']:
                        ips_data[address] = {
                            'ip': address,
                            'type': ip_type,
                            'address_range': subnet['addressRange'],
                            'mask': subnet['addressRange'].split('/')[1],
                            'gateway': subnet['gateway'],
                        }
                        break

            port_ips_data = {}
            for port in router_ports:
                port_ips_data[port['port_id']] = []
                for port_config in port_configs:
                    for port_config_ip in port_config_ips:
                        if port_config_ip['idIPAddress'] == port_config['port_ip_id'] and \
                                port_config['port_id'] == port['port_id']:
                            port_ips_data[port['port_id']].append(ips_data[port_config_ip['address']])

            # oob ip in not stored in db so requesting user to enter and compare it with ip deduced from location
            for port in router_ports:
                if port_rmpf_pfs[port['port_id']][1] == 'OOB':
                    ip = input('Please enter correct OOB IP Address of the router (IPV4): ')
                    if not router_oob_ip == ip:
                        utils.error('Entered OOB IP Address is not correct, please try again.')
                        return
                    utils.colour_print('(colour_success)OK(colour_clear)')
                    utils.colour_print('Entered OOB IP Address is correct and processing...')
                    addr_range = router_oob_ip + '/16'
                    addr_octs = addr_range.split('.')
                    gateway = addr_octs[0] + '.' + addr_octs[1] + '.0.1'
                    ips_data[router_oob_ip] = {
                        'ip': router_oob_ip,
                        'type': 'inet',
                        'address_range': addr_range,
                        'mask': '16',
                        'gateway': gateway,
                    }
                    port_ips_data[port['port_id']] = [ips_data[router_oob_ip]]
                    break

            # Ports and their ips
            label = f'Router #{router_id} ports and IPs'
            utils.colour_print('┌─────────────────────────────────────────────────────────────────────────────────┐')
            utils.colour_print(f'│{label:^81}│')
            utils.colour_print('├────────┬──────────────┬─────────────────────────────┬───────────────────────────┤')
            utils.colour_print('│   ID   │     Name     │          Function           │            IPs            │')
            utils.colour_print('├────────┼──────────────┼─────────────────────────────┼───────────────────────────┤')

            for port in router_ports:
                name = port_rmpf_pfs[port['port_id']][0]
                function = port_rmpf_pfs[port['port_id']][1]
                ips = port_ips_data[port['port_id']]

                for i, ip in enumerate(ips):
                    # proper print
                    if i == 0:
                        utils.colour_print(f'│{port["port_id"]:^8}│{name:^14}│{function:^29}│{ip["ip"]:^27}│')
                        if port_rmpf_pfs[port['port_id']][1] == 'Management':
                            set_data['router']['router_ip'] = ip['ip']
                    else:
                        utils.colour_print(f'│{"":^8}│{"":^14}│{"":^29}│{ip["ip"]:^27}│')

            utils.colour_print('└────────┴──────────────┴─────────────────────────────┴───────────────────────────┘')
            utils.line_break()

            # Gather port data for set config
            for port in router_ports:
                name = port_rmpf_pfs[port['port_id']][0]
                function = port_rmpf_pfs[port['port_id']][1]
                set_data['ports'].append(
                    {
                        'name': name,
                        'function': function,
                        'ip_confs': port_ips_data[port['port_id']],
                    },
                )
            utils.line_break()
            RouterUpdate.update(set_data)

        except:
            utils.error('An error occurred while executing router')
            traceback.print_exc()
