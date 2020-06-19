# stdlib
import subprocess
import getpass
# local
from bin import utils


class Porter:

    def run(self):
        self.porter()

    def porter(self):
        ip = input('What IP do you want to scan: ')
        utils.colour_print('(colour_prompt)Doing TCP First...')
        try:
            results = subprocess.check_output(['nmap', '-Pn', ip])
        except subprocess.CalledProcessError as e:
            utils.error(e.output)

        utils.line_break()
        utils.colour_print('(colour_success)TCP Results')
        utils.colour_print('(colour_clear)' + str(results.decode('utf8')))
        utils.line_break()

        utils.colour_print('(colour_prompt)Now doing UDP...')
        utils.colour_print(
            '(colour_warning)WARNING: '
            '(colour_clear)This will require the sudo password for (colour_rocky)Rocky(colour_clear).')

        password = getpass.getpass('Enter sudo password: ')

        try:
            results = subprocess.check_output(f'echo "{password}" | '
                                              'sudo -S nmap -Pn -sU '
                                              '--host-timeout 5s ' + ip, shell=True)
        except subprocess.CalledProcessError as e:
            utils.error(e.output)

        utils.line_break()
        utils.colour_print('(colour_success)UDP Results')
        utils.colour_print('(colour_clear)' + str(results.decode('utf8')))
        utils.line_break()
