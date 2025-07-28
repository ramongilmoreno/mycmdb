from mycmdb import configure
from pathlib import Path
import os
import logging

logging.basicConfig(level = logging.INFO)

base = Path('./test')
build = './build'
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
              { 'A': 'A1', 'B': 'B2', 'C': 'C1' },
              { 'A': 'A3', 'B': 'B3', 'C': 'C2' },
              { 'A': 'A4', 'B': 'B3' },
              { 'A': 'A5' },
              {            'B': 'B6', 'C': 'C1' },
              { 'A': 'A7', 'B': 'B7' }
            ]
          }
        ]
      },
    "filesystem": {
        "base": base,
        "build": build
      },
    "some_parameters_here": {
      "green_background_cell_function": lambda value, row_values: ['green-background-cell'] if value == 'C1' else None
    }
  })
configuration.run()

