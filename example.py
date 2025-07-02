from mycmdb import configure
from pathlib import Path
import os
import logging

logging.basicConfig(level = logging.INFO)

base = Path('./test')
build = '../build'
if not os.path.isdir(build):
  os.mkdir(build)
build = Path(build)
configuration = configure.configure({
    "data": {
        "tables": [
          {
            "name": "example_table",
            "values": [
              { 'A': 'A1', 'B': 'B1' },
              { 'A': 'A2' }
            ]
          }
        ]
      },
    "filesystem": {
        "base": base,
        "build": build
      }
  })
configuration.run()

