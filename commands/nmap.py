# stdlib
import subprocess
import re
# local
from bin import utils


class Nmap:

    def run(self):
        self.nmap()

    def nmap(self):
        ra = input('What IP Range do you want to scan: ')
        port = input('What port(s) do you want to scan: ')

        try:
            results = subprocess.check_output(['nmap', '-Pn', '-p', port, '--open', ra])
        except subprocess.CalledProcessError as e:
            utils.error(e.output)
            return

        ips = re.findall(r'(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', results.decode('utf8'))
        utils.colour_print(', '.join(ips))
