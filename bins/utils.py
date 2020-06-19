# stdlib
import datetime
# libs
# local


COMMAND_COLOUR = '\033[0m'
DEFAULT_COLOUR = '\033[93m'
PROMPT_COLOUR = '\033[92m'
ROCKY_COLOUR = '\033[1;36m'
SUCCESS_COLOUR = '\033[32m'
WARNING_COLOUR = '\033[91m'


def colour(string: str) -> str:
    """
    Converts string to its coloured version
    """
    string = string.replace('(colour_cmd)', COMMAND_COLOUR)
    string = string.replace('(colour_clear)', DEFAULT_COLOUR)
    string = string.replace('(colour_prompt)', PROMPT_COLOUR)
    string = string.replace('(colour_success)', SUCCESS_COLOUR)
    string = string.replace('(colour_rocky)', ROCKY_COLOUR)
    string = string.replace('(colour_warning)', WARNING_COLOUR)

    return string


def remove_colour(string: str) -> str:
    """
    Removes colour from string
    """
    string = string.replace('(colour_clear)', '')
    string = string.replace('(colour_cmd)', '')
    string = string.replace('(colour_prompt)', '')
    string = string.replace('(colour_rocky)', '')
    string = string.replace('(colour_success)', '')
    string = string.replace('(colour_warning)', '')

    return string


def format(string: str) -> str:
    """
    format is used to get rid of tabs when printing docstrings
    """
    return '\n'.join([x.strip() for x in string.split('\n')])


def colour_print(string: str):
    """
    Prints string in its coloured form
    """
    print(colour(string) + COMMAND_COLOUR)
    write_log(remove_colour(string))


def write_log(string: str):
    dtime = datetime.datetime.now().strftime('%y-%m-%d')
    with open(f'logs/log-{dtime}.txt', 'a') as f:
        f.write(f'{datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")} ' + string + '\n')


def error(string: str):
    """
    Print string with a red ERROR before it
    """
    print(colour('(colour_warning)ERROR:(colour_clear) ' + string))
    write_log(f'{datetime.datetime.now()}' + 'ERROR: ' + remove_colour(string))


def line_break():
    """
    Print a number of equals signs to separate lines
    """
    colour_print('(colour_prompt)' + ('=' * 48) + '(colour_clear)')


def user_input_validate(print_statement):
    """
    Takes the user input twice, compares the two inputs to validate.
    """
    print(print_statement)
    first_value = input('\r -    Enter: ')
    second_value = input('\r - Re-enter: ')
    if first_value == second_value:
        return first_value
    else:
        colour_print(f'(colour_warning)\r # The values entered did not match, please try again.(colour_clear)')
        return False


def create_api_module(cloud):

    # pulls the data from settings file
    cloudcix_api_url = cloud['CLOUDCIX_API_URL']
    cloudcix_api_username = cloud['CLOUDCIX_API_USERNAME']
    cloudcix_api_password = cloud['CLOUDCIX_API_PASSWORD']
    cloudcix_api_key = cloud['CLOUDCIX_API_KEY']
    cloudcix_api_verison = cloud['CLOUDCIX_API_VERSION']
    cloudcix_api_v2_url = cloud['CLOUDCIX_API_V2_URL']

    # create a file containf the information so that it can be used as a module
    setting_module = open('settings_file.py', 'w')
    line = (
        'CLOUDCIX_API_URL = \'%s\'\n'
        'CLOUDCIX_API_USERNAME = \'%s\'\n'
        'CLOUDCIX_API_PASSWORD = \'%s\'\n'
        'CLOUDCIX_API_KEY = \'%s\'\n'
        'CLOUDCIX_API_VERSION = %i\n'
        'CLOUDCIX_API_V2_URL = \'%s\''

        % (
            cloudcix_api_url,
            cloudcix_api_username,
            cloudcix_api_password,
            cloudcix_api_key,
            cloudcix_api_verison,
            cloudcix_api_v2_url,
        )
    )
    setting_module.write(line)
    setting_module.close()
