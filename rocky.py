# stdlib
import sys
import os
import getpass
import subprocess
# local
from bin import utils
import command
import settings


if __name__ == '__main__':
    os.system('clear')

    def start_screen():
        with open('data/splash.txt') as r:
            return r.read()

    def start_text():
        return """
        (colour_clear)Type (colour_cmd)help (colour_clear)or (colour_cmd)? (colour_clear)for command list.
        Type (colour_cmd)help help (colour_clear)to get a detailed list of commands.
        Type (colour_cmd)exit(colour_clear) when finished.
        'Tab autocomplete' and 'Up Arrow history' are supported.
        Press 'Enter' to execute the most recent command again.
        """

    def get_current_git_sha() -> str:
        """
        Finds the current git commit sha and returns it
        :return: The sha of the current commit
        """
        return subprocess.check_output([
            'git',
            'describe',
            '--always',
        ]).strip().decode()

    version = settings.VERSION
    print(utils.colour(start_screen()))
    print(utils.colour(f'\t(colour_rocky)Version {version}'))
    print(utils.colour('\t(colour_prompt)Commit ' + get_current_git_sha()))
    print(utils.colour(utils.format(start_text())))

    if not os.path.exists('logs/'):
        os.mkdir('logs/')
    utils.write_log('Rocky started (Commit ' + get_current_git_sha() + ')')

    PASSWORD = ''

    try:
        # Get network password from user
        while PASSWORD == '':
            PASSWORD = getpass.getpass('Network Password (or exit to quit) ... ')
        if PASSWORD == 'exit':
            print(utils.COMMAND_COLOUR)
            sys.exit()

        # Start command loop
        command.CmdParse(password=PASSWORD).cmdloop()
    except KeyboardInterrupt:
        print(utils.COMMAND_COLOUR)
        sys.exit()
