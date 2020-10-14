#!/usr/bin/env python

import os
import subprocess

if __name__ == '__main__':
    cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cwd_pardir = os.path.dirname(cwd)

    # install dependencies
    subprocess.call([
        'pip',
        'install',
        '-r',
        'requirements-dev.txt',
    ], cwd=cwd_pardir)

    # format code
    subprocess.call([
        'autopep8',
        '-r',
        '--in-place',
        '--aggressive',
        '--aggressive',
        '--max-line-length=79',
        'apps',
    ], cwd=cwd)
    # check code style
    subprocess.call(['flake8', 'apps'], cwd=cwd)

    # start unittest
    subprocess.call(['python', 'manage.py', 'makemigrations'], cwd=cwd)
    subprocess.call(['python', 'manage.py', 'test'], cwd=cwd)
