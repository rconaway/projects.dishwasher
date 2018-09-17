import config.document as document
from typing import List

f = open("/Users/rconaway/etc/nRF5_SDK/examples/peripheral/dishwasher_tilt_ball/pca10056/blank/config/sdk_config.h")
text = f.readlines()
doc = document.parse(text)
out = doc.dump()

fout = open("/tmp/sdk_config.h", "w")

def _display(text):
    if isinstance(text, List):
        for line in text:
            _display(line)
    else:
        fout.write(text + "\n")


_display(out)



