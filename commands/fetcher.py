# stdlib
import getpass
import os
import socket
import subprocess
import time
# lib
import paramiko
# local
from bin import utils, cloud, Hosts
import settings


class Fetcher:

    def __init__(self):
        Hosts.__init__(self)

    def run(self, password: str):
        if not os.path.exists('data/configs/'):
            os.mkdir('data/configs/')
        self.fetcher(password)

    def process_palo_alto_hosts(self, hostname, hostip, host_user, password):
        """
        Process Palo Alto hosts
        """
        hostfile = settings.DEVICE_CONFIG_PATH + hostname

        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(hostip, port=22, username=host_user, password=password)
            except paramiko.AuthenticationException:
                password = getpass.getpass('Error with Password. Please enter Plain Text PW: ')
                client.connect(hostip, port=22, username=host_user, password=password)

            remote_conn = client.invoke_shell()
            remote_conn.send('set cli pager off\n')
            remote_conn.send('show config running\n')
            time.sleep(5)
            conf_data = cloud.recv_timeout(remote_conn)

            try:
                conf_data = conf_data.split('> show config running')[1]
                conf_data = conf_data.split('admin' + hostip + '(active)>')[0]
            except IndexError:
                pass

            print(conf_data)
        except (paramiko.SSHException, socket.error, paramiko.AuthenticationException) as e:
            utils.error(f'Couldn\'t connect to host {hostname}: {e}')
            client.close()
            return
        finally:
            client.close()

        if conf_data:
            with open(hostfile + '.conf', 'w+') as textfile:
                textfile.write(conf_data)

    def process_juno_hosts(self, hostname, hostip, host_user, password):
        """
        Process Juno Hosts
        """
        hostfile = settings.DEVICE_CONFIG_PATH + hostname + '.set'
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostip, port=22, username=host_user, password=password)
            stdin, stdout, stderr = client.exec_command('show configuration | display set')
            output = str(stdout.read().decode('utf8'))

            utils.colour_print(output)

            stdin, stdout, stderr = client.exec_command('show chassis hardware')
            output = output + str(stdout.read().decode('utf8')) + '\n' + '\n'
            utils.colour_print(output)

            stdin, stdout, stderr = client.exec_command('show configuration')
            output = output + str(stdout.read().decode('utf8'))
            utils.colour_print(output)

            with open(hostfile, 'w+') as textfile:
                textfile.write(output)
        except (paramiko.SSHException, socket.error, paramiko.AuthenticationException) as e:
            utils.error(f'Couldn\'t connect to host {hostname}: {e}')
        finally:
            client.close()

    def process_cisco_hosts(self, hostname, hostip, host_user, password):
        """
        Process Cisco Hosts
        """
        hostfile = settings.DEVICE_CONFIG_PATH + hostname + '.conf'
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostip, port=22, username=host_user, password=password)
            stdin, stdout, stderr = client.exec_command('show run')
            output = str(stdout.read().decode('utf8'))

            utils.colour_print(output)

            with open(hostfile, 'w+') as textfile:
                textfile.write(output)
        except (paramiko.SSHException, socket.error, paramiko.AuthenticationException) as e:
            utils.error(f'Couldn\'t connect to host {hostname}: {e.message}')
        finally:
            client.close()

    def print_table(self):
        """
        Print out table detailing command
        """
        print()
        utils.colour_print('(colour_cmd)\u250D' + ('\u2501' * 30) + '\u2511')
        utils.colour_print('\u2502' + (' ' * 30) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 8) + '(colour_clear)Config Fetcher(colour_cmd)' + (' ' * 8) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 2) + '(colour_clear)Backs up Juniper and Cisco(colour_cmd)' + (' ' * 2) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 2) + '(colour_clear)and Palo Alto Hosts to Device(colour_cmd)' + (' ' * 2) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 9) + '(colour_clear)Config repository.(colour_cmd)' + (' ' * 10) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 30) + '\u2502')
        utils.colour_print(
            '\u2515' + ('\u2501' * 30) + '\u2519(colour_clear)')
        print()

    def fetcher(self, password: str):
        """
        Config Fetcher backs up Juniper, Cisco and Palo Alto hosts to Git repository
        """
        self.print_table()

        for host in self.paloalto_hosts:
            utils.colour_print(f"{host['host_name']} {host['ip']} ")

            self.process_palo_alto_hosts(
                host['host_name'],
                host['ip'],
                host['username'],
                password,
            )

            utils.line_break()
            utils.colour_print(
                f'(colour_clear)Palo Alto Host {host["host_name"]} processed!(colour_clear)',
            )
            utils.line_break()
            print()

        utils.line_break()
        print()

        for host in self.juniper_hosts:
            self.process_juno_hosts(
                host['host_name'],
                host['ip'],
                host['username'],
                password,
            )

            utils.line_break()
            utils.colour_print(f'(colour_clear)Junos Host {host["host_name"]} processed!')
            utils.line_break()
            print()

        utils.line_break()
        print()

        for host in self.rocky_hosts:
            self.process_juno_hosts(
                host['host_name'],
                host['ip'],
                host['username'],
                password,
            )
            utils.line_break()
            utils.colour_print(f'(colour_clear)Junos Host {host["host_name"]} processed!')
            utils.line_break()

        utils.line_break()
        print()

        for host in self.cisco_hosts:
            self.process_juno_hosts(
                host['host_name'],
                host['ip'],
                host['username'],
                password,
            )
            utils.line_break()
            utils.colour_print(f'(colour_clear)Cisco Host {host["host_name"]} processed!')
            utils.line_break()
            print()

        utils.colour_print('Push config files to Repository')
        repo_path = settings.DEVICE_CONFIG_PATH
        process_command = f'cd { repo_path };git add -A;git commit -m "Config files updated!"; git push origin master'
        subprocess.call(process_command, shell=True)
