# -*- coding: utf-8 -*-
"""Setup the HelloWorld application"""

import logging
from tg import config
from helloworld import model

import transaction


def bootstrap(command, conf, vars):
    """Place any commands to setup helloworld here"""

    # <websetup.bootstrap.before.auth

    # <websetup.bootstrap.after.auth>
