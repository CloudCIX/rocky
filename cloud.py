# stdlib
import os
import socket
import time
import traceback
# libs
from netaddr import IPNetwork
# local
from . import utils
import settings


def regions():
    """
    Print list of Regions
    """
    # reads the API data from the settings file and creates an .py file dynamically for each cloud
    cloud_data = settings.clouds
    # loop through each cloud and pull the needed data for the api
    for cloud in cloud_data:
        utils.create_api_module(cloud)

        try:
            os.environ.setdefault('CLOUDCIX_SETTINGS_MODULE', 'settings_file')
            from cloudcix import api
            from cloudcix.auth import get_admin_token

            utils.colour_print('(colour_prompt)id\tregion')
            utils.line_break()

            token = get_admin_token()
            response = api.Membership.address.list(
                token=token,
                params={'member_id': 2},
            )
            if response.status_code != 200:
                utils.error('CMDB connection error occurred in routers.')
                return

            if response.json()['_metadata']['total_records'] == 0:
                utils.colour_print('(colour_warning)No record found in the database!')
                return

            names = response.json()['content']
            for name in names:
                regions = name['name']
                id = name['id']
                print(f'{id}\t{regions}')
        except:
            utils.error(f'Couldn\'t connect to CloudCIX API')
            print(traceback.format_exc())
            return


def routers(region_id=0):
    """
    Print list of routers
    """
    # reads the API data from the settings file and creates an .py file dynamically for each cloud
    cloud_data = settings.clouds
    # loop through each cloud and pull the needed data for the api
    for cloud in cloud_data:
        utils.create_api_module(cloud)
        try:
            os.environ.setdefault('CLOUDCIX_SETTINGS_MODULE', 'settings_file')
            from cloudcix import api
            from cloudcix.auth import get_admin_token

            utils.colour_print('idRouter\tregion\tassetTag\tmodelNumber')
            utils.line_break()

            token = get_admin_token()
            params = {}
            if region_id != 0:
                params['region'] = region_id
            response = api.IAAS.router.list(
                token=token,
                params=params,
            )
            if response.status_code != 200:
                utils.error('CMDB connection error occured in routers.')
                return

            if response.json()['_metadata']['totalRecords'] == 0:
                utils.colour_print('(colour_warning)No record found in the database!')

            content = response.json()['content']
            for router in content:
                asset_cmdb = api.Asset.asset.read(token=token, pk=router['idAsset'])
                asset = asset_cmdb.json()['content']
                membership_cmdb = api.Membership.address.read(token=token, pk=asset['idAddress'])
                membership = membership_cmdb.json()['content']
                id_router = router['idRouter']
                region = router['region']
                company_name = membership['companyName']
                asset_tag = asset['assetTag']
                model_number = asset['modelNumber']
                utils.colour_print(f'{id_router}\t{region}\t{company_name}\t{asset_tag}\t{model_number}')
            return

        except:
            utils.error('Couldn\'t connect to CloudCIX API')
            print(traceback.format_exc())


def vm(project_id=0):
    """
    Print list of VMs
    """
    # reads the API data from the settings file and creates an .py file dynamically for each cloud
    cloud_data = settings.clouds
    # loop through each cloud and pull the needed data for the api
    for cloud in cloud_data:
        utils.create_api_module(cloud)
        try:
            os.environ.setdefault('CLOUDCIX_SETTINGS_MODULE', 'settings_file')
            from cloudcix import api
            from cloudcix.auth import get_admin_token

            utils.colour_print('id\tstate\tregion\tcpu\tram\tidProject')
            utils.line_break()

            token = get_admin_token()
            if project_id == 0:
                params = {}
            else:
                params = {'project': project_id}
            response = api.IAAS.vm.list(
                token=token,
                params=params,
            )
            if response.status_code != 200:
                utils.error('CMDB connection error occured in routers.')
                return

            if response.json()['_metadata']['totalRecords'] == 0:
                utils.colour_print('(colour_warning)No record found in the database!')

            content = response.json()['content']
            for vm in content:
                project_cmdb = api.IAAS.project.read(token=token, pk=vm['idProject'])
                project = project_cmdb.json()['content']
                membership_db = api.Membership.address.read(
                    token=token,
                    pk=project['region'],
                )
                membership = membership_db.json()['content']
                if membership['idMember'] != 2:
                    utils.error('VM not in idMember 2')
                    return

                id_vm = vm['idVM']
                state = vm['state']
                region = project['region']
                cpu = vm['cpu']
                ram = vm['ram']
                id_project = vm['idProject']
                utils.colour_print(f'{id_vm}\t{state}\t{region}\t{cpu}\t{ram}\t{id_project}')

        except:
            utils.error('Couldn\'t connect to CloudCIX API ')
            print(traceback.format_exc())


def subnet(region_id=0):
    """
    Print list of Subnets
    """
    # reads the API data from the settings file and creates an .py file dynamically for each cloud
    cloud_data = settings.clouds
    # loop through each cloud and pull the needed data for the api
    for cloud in cloud_data:
        utils.create_api_module(cloud)
        try:
            os.environ.setdefault('CLOUDCIX_SETTINGS_MODULE', 'settings_file')
            from cloudcix import api
            from cloudcix.auth import get_admin_token

            utils.colour_print('idSubnet\tregion\taddressRange\tidVRF\tvLAN\tvxLAN')
            utils.line_break()

            token = get_admin_token()
            if region_id == 0:
                params = {'idMember': 2}
            else:
                params = {'idMember': 2, 'idAddress': region_id}
            response = api.IAAS.subnet.list(
                token=token,
                params=params,
            )
            if response.status_code != 200:
                utils.error('CMDB connection error occured in routers.')
                return

            if response.json()['_metadata']['totalRecords'] == 0:
                utils.colour_print('(colour_warning)No record found in the database!')

            content = response.json()['content']
            for subnet in content:
                address_cmdb = api.Membership.address.read(token=token, pk=subnet['idAddress'])
                region = address_cmdb.json()['content']['companyName']

                id_subnet = subnet['idSubnet']
                address_range = subnet['addressRange']
                id_vrf = subnet['idVRF']
                v_lan = subnet['vLAN']
                vx_lan = subnet['vxLAN']
                utils.colour_print(f'{id_subnet}\t{region}\t{address_range}\t{id_vrf}\t{v_lan}\t{vx_lan}')

        except:
            utils.error('Couldn\'t connect to CloudCIX API')
            print(traceback.format_exc())


def vrf(router_id=0):
    """
    Print list of VRFs
    """
    # reads the API data from the settings file and creates an .py file dynamically for each cloud
    cloud_data = settings.clouds
    # loop through each cloud and pull the needed data for the api
    for cloud in cloud_data:
        utils.create_api_module(cloud)
        try:
            os.environ.setdefault('CLOUDCIX_SETTINGS_MODULE', 'settings_file')
            from cloudcix import api
            from cloudcix.auth import get_admin_token

            utils.colour_print('idVRF\tstate\tidRouter\tidIPVRF')
            utils.line_break()

            token = get_admin_token()
            if router_id == 0:
                params = {}
            else:
                params = {'router': router_id}
            response = api.IAAS.vrf.list(
                token=token,
                params=params,
            )
            if response.status_code != 200:
                utils.error('CMDB connection error occured in routers.')
                return

            if response.json()['_metadata']['totalRecords'] == 0:
                utils.colour_print('(colour_warning)No record found in the database!')

            content = response.json()['content']
            for vrf in content:
                id_vrf = vrf['idVRF']
                state_name = state(vrf['state'])
                id_router = vrf['idRouter']
                ipvr = vrf['idIPVrf']
                if ipvr is None:
                    utils.colour_print(f'{id_vrf}\t{state_name}\t{id_router}\tNone')
                else:
                    ipaddress_cmdb = api.IAAS.ipaddress.read(token=token, pk=ipvr)
                    ipaddress = ipaddress_cmdb.json()['content']
                    vraddress = ipaddress['address']
                    utils.colour_print(f'{id_vrf}\t{state_name}\t{id_router}\t{vraddress}')

        except:
            utils.error('Couldn\'t connect to CloudCIX API')
            print(traceback.format_exc())


def ipaddress(id_vrf=0):
    """
    Print list of IP Addresses
    """
    # reads the API data from the settings file and creates an .py file dynamically for each cloud
    cloud_data = settings.clouds
    # loop through each cloud and pull the needed data for the api
    for cloud in cloud_data:
        utils.create_api_module(cloud)
        try:
            os.environ.setdefault('CLOUDCIX_SETTINGS_MODULE', 'settings_file')
            from cloudcix import api
            from cloudcix.auth import get_admin_token

            utils.colour_print('idSubnet\tState\tPrivate IP\tFloating IP\tidIPVRF')
            utils.line_break()

            token = get_admin_token()
            if id_vrf == 0:
                params = {}
            else:
                params = {'idVRF': id_vrf}
            response = api.IAAS.vrf.list(
                token=token,
                params=params,
            )
            if response.status_code != 200:
                utils.error('CMDB connection error occured in routers.')
                return

            if response.json()['_metadata']['totalRecords'] == 0:
                utils.colour_print('(colour_warning)No record found in the database!')

            content = response.json()['content']
            for ipaddress in content:
                subnet_cmdb = api.IAAS.subnet.read(
                    token=token,
                    pk=ipaddress['idVRF'],
                )
                if subnet_cmdb.status_code != 200:
                    utils.error('No Subnets Found')
                    return
                subnet = subnet_cmdb.json()['content']
                ra = subnet.decode('utf-8').split['/'][1]
                vrf_cmdb = api.IAAS.vrf.read(
                    token=token,
                    pk=subnet['idVRF'],
                )
                vrf = vrf_cmdb.json()['content']

                id_subnet = subnet['idSubnet']
                state_name = state(vrf['state'])
                if ipaddress['IPAddressPrivate'] is None:
                    private_ip = 'None'
                else:
                    private_ip = f'{ipaddress["address"]}/{ra}'
                id_ip_address_fip = ipaddress['idIPAddressFIP']
                ip_vrf = vrf['idVRF']
                utils.colour_print(f'{id_subnet}\t{state_name}\t{private_ip}\t{id_ip_address_fip}\t{ip_vrf}')

        except:
            utils.error('Couldn\'t connect to CloudCIX API')
            print(traceback.format_exc())


def apilist():
    """
    Print list of APIs
    """
    # reads the API data from the settings file and creates an .py file dynamically for each cloud
    cloud_data = settings.clouds
    # loop through each cloud and pull the needed data for the api
    for cloud in cloud_data:
        utils.create_api_module(cloud)
        try:
            os.environ.setdefault('CLOUDCIX_SETTINGS_MODULE', 'settings_file')
            from cloudcix import api
            from cloudcix.auth import get_admin_token

            utils.colour_print('(colour_prompt)idMember 2')
            utils.line_break()

            cmdb = [
                'asn',
                'allocation',
                'blacklist',
                'blacklist_source',
                'image',
                'hypervisor',
                'pool_ip',
                'recordptr',
                'router',
                'subnet',
                'vm',
                'vpn_tunnel',
                'vrf',
                'whitelist',
            ]

            token = get_admin_token()
            for cmdb_id in range(len(cmdb)):
                entities = cmdb[cmdb_id]
                service_to_call = getattr(api, 'IAAS')
                entity_to_call = getattr(service_to_call(), entities)
                response = entity_to_call.list(token=token, params={})
                if response.status_code == 200:
                    try:
                        error_code = response.json()['_metadata']['error_code']
                        utils.colour_print(f'{str(response)} for api.IAAS.{str(entities)}.')
                        utils.colour_print(f'list with error code = (colour_cmd){error_code}')
                    except KeyError:
                        utils.colour_print(f'(colour_cmd){str(response)} for api.IAAS.{str(entities)}')
                else:
                    utils.colour_print(f'{str(response)} for api.IAAS.{str(entities)}.list')

                if response.json()['_metadata']['totalRecords'] == 0:
                    utils.colour_print(f'No record for api.IAAS.{str(entities)}.list found in the database')
                else:
                    utils.colour_print(f'(colour_cmd){str(response)} for api.IAAS.{str(entities)}.list')

        except:
            utils.error('Couldn\'t connect to CloudCIX API')
            print(traceback.format_exc())


def state(s: int) -> str:
    """
    Convert state number to name
    """
    if s >= 0 and s <= 14:
        states = (
            'Ignore',
            'Requested',
            'Building',
            'Unresourced',
            'Running',
            'Quiesce',
            'Quiesced',
            'Resart',
            'Scrub',
            'Scrub_queue',
            'Update',
            'Updating',
            'Quiescing',
            'Restarting',
            'Scrub_prep',
        )
        return states[s]
    elif s is None:
        return 'None'
    else:
        return f'Error: {str(s)}  is not a valid state.'


def valid_ip(address: str) -> bool:
    """
    Returns if address is valid IP
    """
    try:
        socket.inet_aton(address)
        return True
    except:
        utils.error('Not a valid IP Address')
        return False


def valid_ip_range(address: str) -> bool:
    """
    Returns if address is valid IP Range
    """
    address = address.split('/')
    if len(address) == 1:
        return valid_ip(address[0])
    elif len(address) == 2:
        try:
            mask = int(address[1])
        except:
            raise Exception('Malformed Address Range')
        if mask > 32 or mask < 16:
            utils.error('Mask Out of Range')
            return False
        return valid_ip(address[0])
    else:
        return False


def valid_rfc1918(network: str) -> bool:
    """
    Verify an IP Address is in RFC1918
    """
    answer = False

    if IPNetwork(network) in IPNetwork('10.0.0.0/8'):
        answer = True
    elif IPNetwork(network) in IPNetwork('172.16.0.0/12'):
        answer = True
    elif IPNetwork(network) in IPNetwork('192.168.0.0/16'):
        answer = True

    return answer


def valid_rfc5737(network: str) -> bool:
    """
    Verify an IP Address is in RFC5737
    """
    answer = False

    if IPNetwork(network) in IPNetwork('192.0.2.0/24'):
        answer = True
    elif IPNetwork(network) in IPNetwork('198.51.100.0/24'):
        answer = True
    elif IPNetwork(network) in IPNetwork('203.0.113.0/24'):
        answer = True

    return answer


def service_entity_list(service, entity, params, **kwargs):

    # reads the API data from the settings file and creates an .py file dynamically for each cloud
    cloud_data = settings.clouds
    # loop through each cloud and pull the needed data for the api
    for cloud in cloud_data:
        utils.create_api_module(cloud)

        try:
            os.environ.setdefault('CLOUDCIX_SETTINGS_MODULE', 'settings_file')
            from cloudcix import api
            from cloudcix.auth import get_admin_token

            service_to_call = getattr(api, service)
            entity_to_call = getattr(service_to_call, entity)

            response = entity_to_call.list(
                token=get_admin_token(),
                params=params,
                **kwargs,
            )

            if response.status_code != 200:
                utils.error(
                    f'HTTP Error {response.status_code} occured while trying to '
                    f'list instances of {service}.{entity} with the following params: '
                    f'{params}\nResponse from API: {response.content.decode()}')
                return []

            return response.json()['content']

        except:
            utils.error('Couldn\'t connect to CloudCIX API')
            print(traceback.format_exc())


def service_entity_read(service, entity, pk):

    # reads the API data from the settings file and creates an .py file dynamically for each cloud
    cloud_data = settings.clouds
    # loop through each cloud and pull the needed data for the api
    for cloud in cloud_data:
        utils.create_api_module(cloud)

        try:
            os.environ.setdefault('CLOUDCIX_SETTINGS_MODULE', 'settings_file')
            from cloudcix import api
            from cloudcix.auth import get_admin_token

            service_to_call = getattr(api, service)
            entity_to_call = getattr(service_to_call, entity)

            response = entity_to_call.read(
                token=get_admin_token(),
                pk=pk,
            )

            if response.status_code != 200:
                utils.error(
                    f'HTTP Error {response.status_code} occured while trying to '
                    f'list instances of {service}.{entity} with the following pk: '
                    f'{pk}\nResponse from API: {response.content.decode()}')
                return []

            return response.json()['content']

        except:
            utils.error('Couldn\'t connect to CloudCIX API')
            print(traceback.format_exc())


def recv_timeout(the_socket, timeout=2):  # Method to get any sized data
    # make socket non blocking
    the_socket.setblocking(0)
    # total data partwise in an array
    total_data = []
    data = ''
    # beginning time
    begin = time.time()
    while 1:
        # if you got some data, then break after timeout
        if total_data and time.time() - begin > timeout:
            break
        # if you got no data at all, wait a little longer, twice the timeout
        elif time.time() - begin > timeout * 2:
            break
        # recv something
        try:
            data = the_socket.recv(8192).decode()
            if data:
                total_data.append(data)
                # change the beginning time for measurement
                begin = time.time()
            else:
                # sleep for sometime to indicate a gap
                time.sleep(0.1)
        except socket.error:
            pass
    # join all parts to make final string
    return str(''.join(total_data))
