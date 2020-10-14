#!/usr/bin/env python

import os
import subprocess

if __name__ == '__main__':
    cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cwd_pardir = os.path.dirname(cwd)

    format_code_cmd = [
        'autopep8',
        '-r',
        '--in-place',
        '--aggressive',
        '--aggressive',
        '--max-line-length=79',
    ]
    subprocess.call([*format_code_cmd, 'interfaces'], cwd=cwd)
    subprocess.call(['flake8', 'interfaces'], cwd=cwd)

    subprocess.call([*format_code_cmd, 'implements'], cwd=cwd)
    subprocess.call(['flake8', 'implements'], cwd=cwd)

    subprocess.call([*format_code_cmd, 'tests'], cwd=cwd)
    subprocess.call(['flake8', 'tests'], cwd=cwd)

    subprocess.call([
        'python', '-m', 'unittest', 'abei.tests'], cwd=cwd_pardir)
