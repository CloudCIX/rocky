# Python3.6 Version of Rocky

## What is Rocky

Rocky is a CLI based management tool for CloudCIX. 

## How to run

* First clone the repo.
^ Next cd rocky/.
* Finally python3 rocky.py.

## Requirements

apt-get install nmap

## How to use

* Type help at the command line
* Type help <command> to get help on a particular command
* Press Return to rerun the previous command
* Use Tab to auto complete a command

## Adding Commands

* First create a file named command_name.py in the commands directory, rocky/commands/*command_name.py*.
* Then create a class within that file called Command_name.
* Now add a def run(self): method to that class.
* Next go to the rocky/command.py and add a method to CmdParse called
* def do_command_name(self, line):.
* Now add a docstring to the def do_command_name(self, line): to act as a help for the command.
* Then add Command_name().run() to the method above.
* Finally go back to rocky/commands/*command_name.py* and create methods that will operate the intended command.
