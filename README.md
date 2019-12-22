# Python 3.7 Version of Rolly

## What is Rolly

Rolly is a CLI based provisioning and management tool for CloudCIX Cloud software.

Rolly is designed to operate in an out of band (OOB) network, serarated from other CloudCIX networks. Rolly's purpose is to facilitate monitoring, testing, debug and recovery. By convention, Rolly uses OOB addresses that are IPV4, RFC1918 addresses in the form 10.S.R.U/16 where...

*	S represents the Site Number. If you are taking a CloudCIX support contract you will be informed of the S octet to use. Otherwise, you can choose any number you wish between 0 and 255. Each Support Number represents a VPN tunnel used by the CloudCIX support centre to reach the site.
*	R represents the Rack. It can be any number from 1 to 255. If you have a multi-rack SRXPod then it is recommended to number them from 1 upwards sequentially. If you have a site with multiple SRXPods then different R numbers must be used. The R number must be unique within a Site.
*	U represents the U location within the Rack of the device.


## How to run

* First clone the GitHub repo
* Generate an SSH key pair
  * In rolly/data/settings.json file, add SSH public key to the key 'ROLLY_RSA'
* Next cd rolly/
* Run python3 rolly.py


## Requirements

apt-get install nmap

## How to use

* Type help at the command line
* Type help <command> to get help on a particular command
* Press Return to rerun the previous command
* Use Tab to auto complete a command

## Adding Commands

* First create a file named command_name.py in the commands directory, rolly/commands/*command_name.py*.
* Then create a class within that file called Command_name.
* Now add a def run(self): method to that class.
* Next go to the rolly/command.py and add a method to CmdParse called
* def do_command_name(self, line):.
* Now add a docstring to the def do_command_name(self, line): to act as a help for the command.
* Then add Command_name().run() to the method above.
* Finally go back to rolly/commands/*command_name.py* and create methods that will operate the intended command.
