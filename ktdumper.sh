#!/bin/bash

set -e

# TODO: automatically set up virtualenv, run sudo?
python3 ktdumper/ktdumper.py "$@"
