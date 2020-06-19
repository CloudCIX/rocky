# local
from bin import cloud, utils


class Show:

    def run(self, line: str):
        self.show(line.lower())

    def show(self, arg: str):
        if arg == '':
            utils.colour_print(
                'Use (colour_cmd)help show (colour_clear)to see available '
                'subcommands for (colour_cmd)show(colour_clear).')
            return
        split = arg.split()
        if split[0] == 'regions':
            cloud.regions()
        elif split[0] == 'routers':
            if len(split) == 1:
                cloud.routers()
            else:
                try:
                    cloud.routers(int(split[1]))
                except ValueError:
                    utils.error('idProject not valid')
        elif split[0] == 'vms':
            if len(split) == 1:
                cloud.vm()
            else:
                try:
                    if int(split[1]) == 0:
                        utils.error('idProject not valid')
                        return
                    cloud.vm(int(split[1]))
                except ValueError:
                    utils.error('idProject not valid')
        elif split[0] == 'subnets':
            if len(split) == 1:
                cloud.subnet()
            else:
                try:
                    cloud.subnet(int(split[1]))
                except ValueError:
                    utils.error('idRegion not valid')
        elif split[0] == 'apilist':
            cloud.apilist()
        elif split[0] == 'apiread':
            cloud.apiread()
        elif split[0] == 'vrfs':
            if len(split) == 1:
                cloud.vrf()
            else:
                try:
                    cloud.vrf(int(split[1]))
                except ValueError:
                    utils.error('idRouter not valid')
        elif split[0] == 'ipaddress':
            if len(split) == 1:
                cloud.ipaddress()
            else:
                try:
                    cloud.ipaddress(int(split[1]))
                except ValueError:
                    utils.error('idVRF not valid')
        else:
            utils.colour_print('(colour_clear)I didn\'t understand that!')
            utils.colour_print('(colour_clear)Type (colour_cmd)help show (colour_clear)to see valid show commands')
