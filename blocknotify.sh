#!/bin/bash

SCRIPTDIR=${HOME}/Apps/slimcoin-fuseki/acme-minitools

(
  flock -n 9 || exit 1
  cd ${SCRIPTDIR}
  /usr/bin/python3 block2rdf-cli.py -b ${1} -P -L -v
) 9>/var/lock/blocknotify_pub

