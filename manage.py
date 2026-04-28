#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2026 Alessio. All Rights Reserved.
#
# Licensed under the Private Use License.
# This software may only be used for private, non-commercial purposes.
# Redistribution, reproduction, or commercial use is strictly prohibited
# without express written permission from the copyright holder.
#
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
