# libs
from jnpr.junos import Device
from jnpr.junos.exception import (
    CommitError,
    ConfigLoadError,
    ConnectError,
    LockError,
    RpcError,
)
from jnpr.junos.utils.config import Config
import time
# local
from bin import Hosts, utils


class UpdateJunosPW:

    def __init__(self):
        Hosts.__init__(self)

    def run(self, password: str):
        self.password = password
        self.update_junos_pw(password)

    def print_table(self):
        print()
        utils.colour_print('(colour_cmd)\u250D' + ('\u2501' * 39) + '\u2511')
        utils.colour_print('\u2502' + (' ' * 16) + '(colour_warning)WARNING(colour_cmd)' + (' ' * 16) + '\u2502')
        utils.colour_print('\u2515' + ('\u2501' * 39) + '\u2519(colour_cmd)')
        utils.colour_print('\u2502' + (' ' * 39) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 6) + ''
            '(colour_clear)Incorrectly updating network(colour_cmd)' + (' ' * 5) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 5) + ''
            '(colour_clear)passwords may leave the entire(colour_cmd)' + (' ' * 4) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 10) + ''
            '(colour_clear)network unreachable.(colour_cmd)' + (' ' * 9) + '\u2502')
        utils.colour_print('\u2502' + (' ' * 39) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 1) + ''
            '(colour_clear)Network passwords must be longer than(colour_cmd)' + (' ' * 1) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 13) + ''
            '(colour_clear)seven digits.(colour_cmd)' + (' ' * 13) + '\u2502')
        utils.colour_print('\u2502' + (' ' * 39) + '\u2502')
        utils.colour_print(
            '\u2502' + (' ' * 11) + ''
            '(colour_clear)Type (colour_cmd)exit (colour_clear)to exit.(colour_cmd)'
            '' + (' ' * 10) + '\u2502')
        utils.colour_print('\u2502' + (' ' * 39) + '\u2502')
        utils.colour_print('\u2515' + ('\u2501' * 39) + '\u2519(colour_clear)')
        print()

    def update_pass(self, hosts, password):
        for host in hosts:
            try:
                utils.colour_print(f'Connecting to device: {host["host_name"]}')
                utils.line_break()
                dev = Device(host=host['ip'], user=host['username'], password=self.password)
                dev.open()
            except ConnectError as e:
                utils.error(f'Cannot connect to device: {e}')
                utils.colour_print(f'Configuration changes for device {host["host_name"]} unsuccessful!')
                return

            with Config(dev) as cu:
                try:
                    cu.lock()
                except LockError:
                    utils.error('Unable to lock configuration')
                    utils.colour_print(
                        f'Configuration changes for device {host["host_name"]} unsuccessful!',
                    )
                    return

                try:
                    cu.load(
                        'set system login user '
                        f'{host["username"]} authentication plain-text-password-value {password}')
                except ConfigLoadError as err:
                    utils.error(f'Unable to load a (colour_cmd)set (colour_clear) command: {err}')
                    utils.colour_print(
                        f'Configuration changes for device {host["host_name"]} unsuccessful!',
                    )
                    utils.colour_print('Unlocking the configuration')
                    cu.unlock()
                    return

                try:
                    cu.commit(comment='Update by Rocky on ' + time.ctime())
                except CommitError as err:
                    utils.error(f'Unable to commit: {err}')
                    utils.colour_print(
                        f'Configuration changes for device {host["host_name"]}'
                        'successful but unable to commit!')

                    try:
                        utils.colour_print(f'Rolling back the configuration device {host["host_name"]}')
                        cu.rollback(rb_id=1)
                        utils.colour_print('Committing the configuration')
                        cu.commit()
                    except CommitError as err:
                        utils.error(f'Unable to commit configuration: {err}')
                        cu.unlock()
                        return
                    except RpcError as err:
                        utils.error(f'Unable to rollback configuration changes: {err}')
                        cu.unlock()
                        return

                try:
                    cu.unlock()
                except LockError as err:
                    utils.error(f'Unable to unlock configuration: {err}')
                finally:
                    dev.close()
        utils.colour_print(
            '(colour_clear)Password change for junos device {juniper_host_name[i]}'
            '(colour_success)successful(colour_clear)!')
        print()

    def update_junos_pw(self, password: str):

        new_pass, new_pass_confirm = '', ' '
        while new_pass != new_pass_confirm or len(new_pass) < 8:
            utils.line_break()
            new_pass = input('Enter the new network password: ')
            if new_pass.lower() == 'exit':
                return
            new_pass_confirm = input('Re-enter the new network password: ')

        self.update_pass(self.juniper_hosts, new_pass)

        self.update_pass(self.rocky_hosts, new_pass)
