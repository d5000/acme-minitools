#!/bin/bash
pushd /opt/acme/slimcoin-acme/acme/scripts
/opt/acme/slimcoin-acme/bin/python3 blocknotify-catchup.py
popd
