# stdlib
import json
from time import asctime, sleep
import traceback
# libs
import jinja2
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError, LockError, ConfigLoadError, CommitError
from jnpr.junos.utils.config import Config
from jnpr.junos.utils.start_shell import StartShell
from jnpr.junos.utils.sw import SW
# local
from . import cloud
from . import utils

__all__ = [
    'RouterMixin',
]
MAX_ATTEMPTS = 3
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('data/templates'),
    trim_blocks=True,
)


class RouterMixin:

    @classmethod
    def scrub(cls, set_data):
        """
        Setups new routers.
        """
        utils.colour_print(f'Generating JunOS setconf for router:')
        file_name = f'scrub.j2'
        setconf = jinja_env.get_template(file_name).render(**set_data)

        if cls.deploy(setconf=setconf, router_ip=set_data['router']['router_ip']):
            utils.colour_print('(colour_success)Successfully scrubbed router.(colour_clear)')
            utils.colour_print('Reboot required so rebooting the router..')

            with Device(host=set_data['router']['router_ip'], user='rocky') as router:
                sw = SW(router)
                sw.reboot(in_min=2)
            utils.colour_print('Rebooting the router...')

        else:
            utils.error('Failed to build router, please try again.')
            traceback.print_exc()

    @classmethod
    def update(cls, set_data):
        """
        Updates router in the region with existing virtual routers in stable states 4, 6.
        state 3 and 9 are ignored.
        states 1, 5, 7, 8, 10 are taken care by Robot.
        But doesn't update if there are VRFs in state 2,11,12,13,14 in the router.
        """
        # Check if any progress state VRFs in the router
        router_id = set_data['router']['router_id']
        vrfs = cloud.service_entity_list('IAAS', 'vrf', {'router': router_id, 'state__in': [2, 11, 12, 13, 14]})
        if vrfs:
            utils.error('There are VRFs in Progress states [2, 11, 12, 13, 14] in the router, so cannot be updated.')
            return
        utils.colour_print('The router is ready to update.')
        utils.colour_print(f'Generating JunOS setconf for router idRouter:{router_id}')
        # gathering base setup set config
        setconf = jinja_env.get_template('scrub.j2').render(**set_data)
        # gathering all virtual routers set config
        for vr in set_data['vrs']:
            setconf = f'{setconf}\n{jinja_env.get_template("vr.j2").render(**vr)}\n'
            # state = 6 vr needs be kept quiesced.
            if vr['state'] == 6:
                setconf = f'{setconf}\n{jinja_env.get_template("quiesce.j2").render(project_id=vr["project_id"])}\n'

        if cls.deploy(setconf=setconf, router_ip=set_data['router']['router_ip']):
            utils.colour_print('(colour_success)Successfully built Router.(colour_clear)')
        else:
            utils.error('Failed to build router, please try again.')
            traceback.print_exc()

    @classmethod
    def deploy(cls, setconf: str, router_ip: str, ignore_missing: bool = False) -> bool:
        """
        Deploy the generated configuration to the Router and return whether or not the deployment succeeded
        :param setconf: The configuration for the virtual router
        :param router_ip: The ip of the physical router to deploy to
        :param ignore_missing: Flag stating whether or not we should ignore the `statement not found` error
        :return: A flag stating whether or not the deployment was successful
        """
        try:
            # Using context managers for Router and Config will ensure everything is properly cleaned up when exiting
            # the function, regardless of how we exit the function
            with Device(host=router_ip, user='rocky', port=22) as router:
                router.timeout = 15 * 60  # 15 minute timeout
                utils.colour_print(f'Successfully connected to Router {router_ip}, now attempting to load config')

                for attempt in range(MAX_ATTEMPTS):
                    try:
                        return cls._configure(setconf, router_ip, router, ignore_missing)
                    except LockError:
                        utils.error(
                            f'Unable to lock config on Router {router_ip}. (Attempt #{attempt + 1} / 3)',
                        )
                        traceback.print_exc()
                        sleep(45)
                utils.error(
                    f'3 attempts to lock Router {router_ip} have failed. This request is now considered a failure.',
                )
                return False
        except ConnectError:
            utils.error(f'Unable to connect to Router {router_ip}')
            traceback.print_exc()
            return False

    @classmethod
    def _configure(cls, setconf: str, router_ip: str, router: Device, ignore_missing: bool) -> bool:
        """
        Open the configuration for the router and attempt to deploy to the router.
        This has been turned into a method to make it easier to repeat this function multiple times.
        :param setconf: The configuration for the virtual router
        :param router_ip: The ip of the physical router to deploy to
        :param router: A Device object representing the Router being configured.
        :param ignore_missing: Flag stating whether or not we should ignore the `statement not found` error
        :return: A flag stating whether or not the deployment was successful
        """
        with Config(router, mode='exclusive') as config:
            try:
                print(setconf)
                config.load(setconf, format='set', merge=True, ignore_warning=ignore_missing)
                utils.line_break()
            except ConfigLoadError as err:
                router.timeout = 2 * 60
                utils.error(
                    f'Unable to load configuration changes onto Router {router_ip} :\n {err}',
                )
                return False

            # Attempt to commit
            try:
                commit_msg = f'Loaded by robot at {asctime()}.'
                utils.colour_print(
                    f'All commands successfully loaded onto Router {router_ip}, '
                    'now checking the commit status',
                )
                # Commit check either raises an error or returns True
                config.commit_check()
                utils.colour_print(f'Commit check on Router {router_ip} successful, committing changes.')
                if not ignore_missing:
                    detail = config.commit(
                        comment=commit_msg,
                    )
                else:
                    detail = config.commit(
                        comment=commit_msg,
                        ignore_warning=['statement not found'],
                    )
                utils.colour_print(f'Response from commit on Router {router_ip}\n{detail}')
            except CommitError as err:
                # Reduce device timeout so we're not waiting forever for it to close config
                router.timeout = 2 * 60
                utils.error(f'Unable to commit changes onto Router {router_ip}:  \n {err}')
                return False
            return True

    @staticmethod
    def run_cmd(router_ip: str, cmd: str) -> str or bool:
        """
        This function sshes into router, runs cmd and brings the output.
        """
        # SSHing into router
        try:
            with Device(host=router_ip, user='rocky', port=22) as router:
                with StartShell(router) as ss:
                    response = ss.run(cmd)
        except Exception as err:
            utils.error(
                f'Error occurred when running cmd# \n{cmd}\n in router @ {router_ip}, #error:\n {err}',
            )
            return False
        return response[1]

    @classmethod
    def router_model(cls, router_ip: str) -> str or bool:
        """
        Fetches router model.
        """
        cmd = 'cli -c "show chassis hardware | display json | no-more"'
        output = cls.run_cmd(router_ip, cmd)
        if output:
            # extracting json string
            data = str(output).split('{', 1)[1].rsplit('}', 1)[0]
            data = json.loads(f'{{{data}}}')
            router_model = data['chassis-inventory'][0]['chassis'][0]['description'][0]['data']
            return router_model
        else:
            return False

    @classmethod
    def root_encrypted_password(cls, router_ip: str) -> str or bool:
        """
        Fetches root encrpted password.
        """
        cmd = 'cli -c "show configuration system root-authentication"'
        output = cls.run_cmd(router_ip, cmd)
        if output:
            # extracting encrypted password line
            password = str(output).split('\r\n')[1].split('"')[1]
            return password
        else:
            return False
