# stdlib
import logging
# libs
import simplejson as json
# local
import settings


class Hosts:
    """
    Desc: Reads Juno host files for juno configs, and it inherited by the following commands

    Commands:
        - alarmer
        - checker
        - fetcher
        - uptime
        - learner
        - update_junos_pw
    """
    def __init__(self):
        try:
            dynamic = settings.HOSTS
            with open(dynamic, 'r') as json_data:
                hosts = json.load(json_data)

            self.cisco_hosts = hosts['cisco_hosts']
            self.juniper_hosts = hosts['juniper_hosts']
            self.paloalto_hosts = hosts['paloalto_hosts']
            self.rocky_hosts = hosts['rocky_hosts']

            self.port = 22

        except(FileNotFoundError):
            logging.error('Unable to open dynamic file', exc_info=True)
            return None
