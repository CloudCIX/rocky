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


class Alarmer(Hosts):
    """
    Command: alarmer

    Desc: inherits from Hosts to get access to juno hosts
    """
    def __init__(self):
        Hosts.__init__(self)

    def proccessJunoAlarm(self, hostname: str, host_ip: str, host_user: str, password: str, alarms: int) -> int:

        line_break()
        print(hostname)

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

            stdin, stdout, stderr = client.exec_command('show chassis alarms')
            output = stdout.read()
            str_output = str(output.decode('utf8'))
            stderr.read()

            if 'No alarms currently active' in str_output:

                colour_print(f'(colour_prompt){str_output}(colour_cmd)')
                alarmout = alarms

            else:

                alarmout = alarms + 1

                colour_print(f'(colour_warning){str_output}(colour_cmd)')

        except(paramiko.SSHException, socket.error):
            colour_print(f'(colour_warning)Error connecting to host {hostname}:(colour_cmd)\n')
            alarmout = alarms + 1

        finally:
            client.close()

        return alarmout

    def alarmer(self, password: str):

        alarms = 0

        for host in self.juniper_hosts:

            alarms = (
                self.proccessJunoAlarm(
                    host['host_name'],
                    host['ip'],
                    host['username'],
                    password,
                    alarms,
                )
            )

        for host in self.rocky_hosts:

            alarms = (
                self.proccessJunoAlarm(
                    host['host_name'],
                    host['ip'],
                    host['username'],
                    password,
                    alarms,
                )
            )

        line_break()

        if alarms == 0:

            colour_print('(colour_prompt)No devices showing alarms. (colour_cmd)')

        else:
            colour_print(f'(colour_warning){alarms}devices show alarms. (colour_cmd)')

        line_break()

    def run(self, password: str):
        self.alarmer(password)
