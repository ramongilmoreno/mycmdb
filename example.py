from mycmdb import configure
from fs import open_fs
import os
import logging

logging.basicConfig(level = logging.INFO)

base = open_fs('./test')
build = '../build'
if not os.path.isdir(build):
  os.mkdir(build)
build = open_fs(build)
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

