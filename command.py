# stdlib
import sys
import cmd
# local
from bin import utils
from commands import (
    Alarmer,
    Checker,
    Fetcher,
    Learner,
    Nmap,
    Ping,
    Porter,
    RouterScrub,
    # RouterUpdate,
    Show,
    UpdateJunosPW,
    Uptime,
)


class CmdParse(cmd.Cmd):

    def __init__(self, password: str, completekey='tab', stdin=None, stdout=None):
        self.password = password
        return super().__init__(completekey, stdin, stdout)

    def do_help(self, arg):
        """
        (colour_clear)
        List available commands with 'help' or detailed help with 'help cmd'.
        ============================================================================
        (colour_prompt)NOC Tools(colour_cmd)
        alarmer        (colour_clear) Scan every network device for hardware alarms.(colour_cmd)
        checker        (colour_clear) Compare every switchport state against learned states.(colour_cmd)
        fetcher        (colour_clear) Collect Configurations and push to Git repository(colour_cmd)
        learner        (colour_clear) Learn every switchport state.(colour_cmd)

        (colour_prompt)SOC Tools(colour_cmd)
        nmap           (colour_clear) Check a range of ports for a range of IPs.(colour_cmd)
        ping           (colour_clear) Ping a range of IP Addresses.(colour_cmd)
        porter         (colour_clear) Check if a port is open on a range of IPs.(colour_cmd)

        (colour_prompt)CloudCIX Tools(colour_cmd)
        router_scrub   (colour_clear) Deploys a new SRX router, or scrubs an old one, in a Region.(colour_cmd)
        router_update  (colour_clear) Updates a new SRX router, or old one, with setup and VRFs in a Region.(colour_cmd)
        show           (colour_clear) Show instances of CloudCIX Objects.(colour_cmd)

        exit           (colour_clear) Exit from Rocky.(colour_cmd)
        """
        if arg:
            try:
                getattr(self, f'help_{arg}')
            except AttributeError:
                try:
                    doc = getattr(self, f'do_{arg}').__doc__
                    if doc:
                        doc = utils.colour(doc)
                        self.stdout.write(f'{utils.format(doc)}\n')
                        return
                except AttributeError:
                    pass
                nohelp = self.nohelp % (arg)
                self.stdout.write(f'{nohelp}\n')
        else:
            super().do_help(arg)

    prompt = utils.colour('(colour_prompt)rocky> (colour_clear)')

    def precmd(self, line):
        utils.write_log('> ' + line)
        return super().precmd(line)

    # Alarmer

    def do_alarmer(self, line):
        """
        Use (colour_cmd)alarmer (colour_clear)to check for hardware alarms on network equipment.
        """
        Alarmer().run(self.password)

    # Checker
    def do_checker(self, line):
        """
        Use (colour_cmd)checker (colour_clear)to compare the current state of every switchport
        to its state learned by (colour_cmd)learner(colour_clear).
        """
        Checker().run(self.password)

    # Learner

    def do_learner(self, line):
        """
        Use (colour_cmd)learner (colour_clear)to learn the state of every switchport.
        It is vital that you run (colour_cmd)checker (colour_clear)before running
        (colour_cmd)learner (colour_clear)and ensure
        that all changes can be accounted for.
        """
        Learner().run(self.password)

    # Fetcher
    def do_fetcher(self, line):
        """
        Use (colour_cmd)fetcher (colour_clear)to collect configurations and push to Git repository.
        """
        Fetcher().run(self.password)

    # Nmap
    def do_nmap(self, line):
        """
        Use (colour_cmd)nmap (colour_clear)to search for a range of open ports in a range of IPs.
        Example valid port ranges are; -100, 200-1024, t:3000-4000, u6000-
        """
        Nmap().run()

    # Ping
    def do_ping(self, line):
        """
        Use (colour_cmd)ping (colour_clear)to ping a range of IPs.
        Syntactically correct examples include...
        ping 91.103.0.1
        ping 91.103.0.1/30
        """
        Ping().run(line)

    # Porter
    def do_porter(self, line):
        """
        Use (colour_cmd)porter (colour_clear)to find all open ports for one IP.
        """
        Porter().run()

    # UpdateJunosPW
    def do_update_junos_pw(self, line):
        """
        Use (colour_cmd)updatejunosPW (colour_clear)to update the Network Password
        """
        UpdateJunosPW().run(self.password)

    # Uptime
    def do_uptime(self, line):
        """
        Use (colour_cmd)uptime (colour_clear)to check...
        a) How long since equipment was rebooted.
        b) System time.
        c) How long since last config commit.
        """
        Uptime().run(self.password)

    # RouterScrub
    def do_router_scrub(self, line):
        """
        Use (colour_cmd)RouterScrub (colour_clear)to initialise an SRX router in preparation
        for installation in a CloudCIX region. The existing configuration will be erased.
        """
        RouterScrub().run()

    # RouterUpdate
    # def do_router_update(self, line):
    #     """
    #     Use (colour_cmd)routerUpdate (colour_clear)to update an SRX router in preparation
    #     to consume router setup changes in a CloudCIX region. The existing configuration will be erased and rebuild.
    #     """
    #     RouterUpdate().run()

    # Show
    def do_show(self, line):
        """
        Use 'show' commands to list Objects in CloudCIX

        (colour_prompt)API (colour_clear)
        show apiRead            Exercises IaaS API read methods and verifies if CloudCIX is working.
        show apiList            Exercises IaaS API list methods and verifies if CloudCIX is working.

        (colour_prompt)Regions (colour_clear)
        show regions            Displays a list of all Regions in CloudCIX.

        (colour_prompt)Routers (colour_clear)
        show routers            Displays a list of all Physical Routers in CloudCIX.
        show routers 85         Displays a list of all Physical Routers in Region 85.

        (colour_prompt)Virtual Routers (colour_clear)
        show vrfs               Displays a list of all VRFs in CloudCIX.
        show vrfs 32            Displays a list of all VRFs in router 32.

        (colour_prompt)Floating Subnets (colour_clear)
        show subnets            Displays a list of CloudCIX floating subnets.
        show subnets 2          Displays a list of all the floating subnets for region 2.

        (colour_prompt)Virtual Machines (colour_clear)
        show vms                Displays a list of all the Virtual Machines.
        show vms 2              Displays a list of all the Virtual Machines for idProject 2.

        (colour_prompt)NAT (colour_clear)
        show ipaddress          Displays a list of all inbound NAT rules in CloudCIX.
        show ipaddress 106      Displays a list of all NAT rules for Virtual router 106.
        """
        Show().run(line)

    # Exit

    def do_exit(self, line):

        """
        Use (colour_cmd)exit (colour_clear)to exit (colour_rocky)Rocky(colour_clear).
        """
        utils.colour_print('(colour_warning)Exiting...')
        print(utils.COMMAND_COLOUR)
        sys.exit()
