#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

if __name__ == '__main__':
    sys.argv = ['manage.py', 'makemigrations']
    execute_from_command_line(sys.argv)
    
    # Now run migrate
    sys.argv = ['manage.py', 'migrate']
    execute_from_command_line(sys.argv)
