#!/usr/bin/env python
import os
import django
import subprocess
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Run makemigrations with input '2' to ignore the saleitem issue
proc = subprocess.Popen(
    [sys.executable, 'manage.py', 'makemigrations', 'api'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True
)

# Send '2' to select "Ignore for now" option
stdout, _ = proc.communicate(input='2\n')
print(stdout)
sys.exit(proc.returncode)
