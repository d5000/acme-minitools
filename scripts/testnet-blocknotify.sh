#!/bin/bash
BLOCKHASH="$@" /opt/acme/slimcoin-acme/bin/python3 /opt/acme/slimcoin-acme/acme/scripts/testnet-blocknotify.py  > /opt/acme/log/blocknotify.log 2>&1
echo "${@}" >> /opt/acme/log/slm-blocknotify.log

