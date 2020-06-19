# stdlib
import socket
# libs
import paramiko
# local
from bin import Hosts
from bin.utils import (
    colour_print,
    line_break,
)


class Uptime(Hosts):
    """
    Command: uptime

    Desc: inherits from Hosts to get access to juno hosts to gather there uptime information
    """
    def __init__(self):
        Hosts.__init__(self)

    def processJunosUptime(self, hostname: str, host_ip: str, host_user: str, password: str):

        print(hostname, '=' * (40 - len(host_ip)))

        # Show system uptime, last commit etc.
        try:

            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            client.connect(
                hostname=host_ip,
                port=self.port,
                username=host_user,
                password=password,
            )

            stdin, stdout, stderr = client.exec_command('show system uptime')
            output = stdout.read()
            str_output = str(output.decode('utf8'))
            stderr.read()

            colour_print(f'(colour_clear){str_output}(colour_cmd)')

        except(paramiko.SSHException, socket.error):
            pass

        finally:
            client.close()

    def uptime(self, password: str):

        for host in self.rocky_hosts:

            self.processJunosUptime(
                host['host_name'],
                host['ip'],
                host['username'],
                password,
            )

        line_break()

        for host in self.juniper_hosts:

            self.processJunosUptime(
                host['host_name'],
                host['ip'],
                host['username'],
                password,
            )

        line_break()

    def run(self, password: str):

        self.uptime(password)
