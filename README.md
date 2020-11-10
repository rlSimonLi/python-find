# python-find
Python implementation of the Linux find command.

This command allows you to search the file system namespace for a file that satisfies some criteria.

# Usage
`find.py [--regex=pattern | --name=filename] directory [command]`

`directory` is a required argument for the path to the directory to traverse.

`filename` is the exact filename to match against when traversing the directory pattern is the regular expression pattern to match against when traversing the directory.

`command` is an optional argument which is a Unix command that has {} in the command string replaced by the filename that is currently being executed on.
