#!/usr/bin/env python3

import config.document as document
from typing import List
import sys

if not sys.argv[1]:
    print ("usage: list_config.py {config-file}")
    sys.exit(-1)

f = open(sys.argv[1])
text = f.readlines()
doc = document.parse(text)

out = doc.dump()
for line in out:
    print(line)
