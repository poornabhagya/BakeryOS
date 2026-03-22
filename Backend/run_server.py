#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

if __name__ == '__main__':
    django.setup()
    from django.core.management import call_command
    call_command('runserver', '0.0.0.0:8000')
