#!/usr/bin/env python3

import config.document as document
from typing import List
import sys

if len(sys.argv) < 1:
    print ("usage: list_config.py {config-file}")
    sys.exit(-1)

doc = document.parse_file(sys.argv[1])
doc.print()
