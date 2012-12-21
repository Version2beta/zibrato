#!/usr/bin/env python

import sys
import os
import argparse
sys.path.append("..")
sys.path.append(os.path.join(sys.path[0], ".."))
import zibrato

HOSTNAME = "metrics-api.librato.com"
APIPATH = "/v1/"

parser = argparse.ArgumentParser(description='Connect zibrato to Librato.')
parser.add_argument('--username', required=True)
parser.add_argument('--apikey', required=True)
parser.add_argument('--hostname', default=HOSTNAME)
parser.add_argument('--apipath', default=APIPATH)
parser.add_argument('-v', '--version')
args = parser.parse_args()

print args
