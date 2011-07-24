#!/usr/bin/env python


import sys
from rmtoo.lib import RmtooMain


def main():
    """ Entry point for using with tools like buildout.

    Replacement for script ``bin/rmtoo``.
    """

    RmtooMain.main(sys.argv[1:], sys.stdout, sys.stderr)
