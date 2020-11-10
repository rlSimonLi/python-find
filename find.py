#!/usr/bin/python3

import os
import re
import sys

USAGE = "Usage: myfind [--regex=pattern | --name=filename] directory [command]"
ERROR = "Error: Unable to start process '{}'"


def parse_args(args):
    """Returns a tuple of (directory, regex, filename, command)"""
    directory = None
    regex = None
    filename = None
    command = None

    for arg in args[1:]:
        # if matches if either flag is contained in the arguments
        regex_match = re.search(r"--regex=(.*)", arg)
        filename_match = re.search(r"--name=(.*)", arg)
        if regex_match or filename_match:
            if regex_match:
                regex = regex_match.group(1)
            if filename_match:
                filename = filename_match.group(1)
        else:
            # If directory has not been assigned a value, this parameter must be directory
            if directory:
                command = arg
            # If directory is already assigned a value, that means this is the second non-flag parameter
            else:
                directory = arg

    # raise an error if both flags are provided
    if regex and filename:
        raise ValueError
    # raise an error if directory is not provided
    if not directory:
        raise ValueError

    return directory, regex, filename, command


def get_path_list(directory, parameter=None, mode=None):
    """
    Returns a list of paths for every file/directory under that directory.
    If a mode is provided, a list of paths that satisfy the matching will be returned.
    Modes are regex and name
    """
    # exit with usage message if the directory doesn't exit
    if not os.path.exists(directory):
        print(USAGE, file=sys.stderr)
        sys.exit(1)
    paths = []
    # replace tilde with the actual home directory
    directory.replace("~", os.path.expanduser("~"))
    # add the directory itself to the paths list
    if is_match(directory.split("/")[-1], parameter, mode):
        paths.append(directory)

    for root, directories, files in os.walk(directory):
        # loops through file names in a directory
        for name in files:
            new_path = os.path.join(root, name)
            if is_match(name, parameter, mode):
                paths.append(new_path)
        # loops through sub-directories names in a directory
        for name in directories:
            new_path = os.path.join(root, name)
            if is_match(name, parameter, mode):
                paths.append(new_path)

    return paths


def is_match(name, parameter, mode=None):
    """Returns a boolean value of whether the path has a match"""
    # return true if no mode is provided (regardless what the path is)
    if not mode:
        return True
    if mode == "regex":
        try:
            if re.search(parameter, name):
                return True
        # exit with usage message if regular expression is not legal
        except re.error:
            print(USAGE, file=sys.stderr)
            sys.exit(1)
    if mode == "name":
        if name == parameter:
            return True

    return False


def execute_command(path, command):
    """execute the command with the path"""
    args = command.split(" ")
    for i in range(len(args)):
        # replace all {} with the path in the argument
        if "{}" in args[i]:
            args[i] = args[i].replace("{}", path)
    os.execlp(args[0], *args)


def find(argv):
    """A simplified find command."""
    try:
        directory, regex, filename, command = parse_args(sys.argv)
    # if any of the checks in parse_args() fail, exit with usage message
    except ValueError:
        print(USAGE, file=sys.stderr)
        sys.exit(1)

    if regex:
        paths = get_path_list(directory, regex, "regex")
    elif filename:
        paths = get_path_list(directory, filename, "name")
    else:
        paths = get_path_list(directory)

    if command:
        failed = False
        for path in paths:
            pid = os.fork()
            # only child processes execute this bit
            if pid == 0:
                try:
                    execute_command(path, command)
                except (PermissionError, IOError):
                    # exiting from child process
                    os._exit(1)
            # only parent process execute this bit
            else:
                # get child process exit status, this can come from the command itself or the exception handling above
                exit_status = os.wait()[1]
                # prints process error to parent's stderr if the exit status of child process is not 0
                if exit_status != 0:
                    print(ERROR.format(command.replace("{}", path)), file=sys.stderr)
                    # changes flag if any child process fails
                    failed = True

        # exit with nonzero if any child process failed, otherwise exit with zero (by default)
        if failed:
            sys.exit(1)

    # just print the path if not instructed to execute commands
    else:
        for path in paths:
            print(path)


if __name__ == "__main__":
    find(sys.argv)
