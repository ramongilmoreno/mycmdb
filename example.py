from mycmdb import configure, transformations
from pathlib import Path
import os
import logging
import math

logging.basicConfig(level = logging.INFO)

base = Path('./test')
build = './build'
if not os.path.isdir(build):
  os.mkdir(build)
build = Path(build)

def fibonacci (input):
  if input == 0:
    return 0
  elif input == 1:
    return 1
  else:
    return fibonacci(input - 1) + fibonacci(input - 2)
# https://en.wikipedia.org/wiki/Fibonacci_sequence#Computation_by_rounding
def log_phi (input):
  return math.log(input) / math.log((1 + math.sqrt(5)) / 2)
def fibonacci_index (input):
  if input == None:
    return None
  if input == 0:
    return 0
  elif input == 1:
    return 1
  else:
    return math.floor(log_phi(math.sqrt(5) * (input + 0.5)))

configuration = configure.configure({
    "data": {
        "tables": [
          {
            "name": "example_table",
            "values": [
              { 'A': 'A1', 'B': 'B1',            'Fibonacci': fibonacci(0) },
              { 'A': 'A1', 'B': 'B2', 'C': 'C1', 'Fibonacci': fibonacci(1) },
              { 'A': 'A3', 'B': 'B3', 'C': 'C2', 'Fibonacci': fibonacci(2) },
              { 'A': 'A4', 'B': 'B3',            'Fibonacci': fibonacci(3) },
              { 'A': 'A5',                       'Fibonacci': fibonacci(4) },
              {            'B': 'B6', 'C': 'C1', 'Fibonacci': fibonacci(5) },
              { 'A': 'A7', 'B': 'B7',            'Fibonacci': fibonacci(6) }
            ],
            "typed_columns": {
              "Fibonacci": "NUMBER"
            }
          }
        ],
        "sql_functions": [
          # Triplet with function name and actual function
          ( "prefix_it", lambda input: f"Prefixed: {str(input)}" if input else None ),
          ( "fibonacci_index", fibonacci_index )
        ]
      },
    "filesystem": {
        "base": base,
        "build": build
      },
    "production": {
        "transformation": transformations.transformation_builder(
            transformations.to_xml,
            transformations.page_orientation,
            transformations.markdown_tags,
            transformations.from_xml
          )
      },
    "some_parameters_here": {
      "green_background_cell_function": lambda value, row_values: ['green-background-cell'] if value == 'C1' else None
    }
  })
configuration.run()

