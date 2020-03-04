"""Main"""

import sys
import os
from cpu import CPU

# if len(sys.argv) != 2:
#     print("ERR: No file given:\t python ls8.py examples/file_name")
#     sys.exit(1)

# script_dir = os.path.dirname(__file__)
# file_name = sys.argv[1]
# arg handed should be a file path ex: examples/file_name
# file_path = os.path.join(script_dir, file_name)

cpu = CPU()
cpu.load("well_message.txt")
cpu.run()
