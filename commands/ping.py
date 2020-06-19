# libs
import netaddr
import sh
# local
from bin import utils, cloud


class Ping:

    def run(self, line: str):
        self.ping(line)

    def ping(self, param):
        if not cloud.valid_ip_range(param):
            utils.error('Invalid IP Address Range')
            return

        utils.colour_print('(colour_clear)Now scanning:(colour_prompt) ' + param)
        try:
            ipset = netaddr.IPSet([param])
        except (netaddr.AddrFormatError, netaddr.AddrConversionError):
            utils.error('Invalid IP Address Range')
            return

        for ip in ipset:
            try:
                sh.ping(ip, '-w1 -c1')
                utils.colour_print('(colour_clear)Ping to ' + str(ip) + ' (colour_success)OK(colour_clear)')
            except sh.ErrorReturnCode_1:
                utils.error('No response from ' + str(ip))
            except sh.ErrorReturnCode_2 as e:
                utils.error('Error from ping command: ' + e.stderr.decode())
