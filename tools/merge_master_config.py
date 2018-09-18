#!/usr/bin/env python3

import os
import sys
from config import document

SDK = os.environ["SDK"]
if not SDK:
    SDK = "/Users/rconaway/etc/nRF5_SDK"

if len(sys.argv) < 1:
    print("usage: merge_master_config.py {config-file}")
    sys.exit(-1)

master = document.parse_file(f"{SDK}/config/nrf52840/config/sdk_config.h")
doc = document.parse_file(sys.argv[1])

# master_kv = master.key_values()
# doc_kv = doc.key_values()
#
# for k in doc_kv.keys():
#     if not k in master_kv.keys():
#         print(k)

