import sqlite3
import logging

logger = logging.getLogger(__name__)

class Data:
  def __init__ (self, configuration, parameters):
    logger.debug('Creating Data object...')
    self.configuration = configuration
    self.parameters = {} if not parameters else parameters

    self.database_connection = sqlite3.connect(':memory:')
    self.cursor = self.database_connection.cursor()

    exclude_order_column = False
    if self.parameters.get('exclude_order_column') == True:
      exclude_order_column = True

    # Create table data
    for table in parameters.get('tables'):
      # Table name
      table_name = table['name']
      if table_name == None:
        logger.error(f'Found table without name {str({} | table)}')
        continue

      # Compute types of columns
      # See https://www.sqlite.org/datatype3.html for detaiils
      typed_columns = {}
      def empty_list (arg):
        return [] if not arg else arg
      for typed_column in empty_list(table.get('typed_column')):
        typed_columns[typed_column] = table['typed_column'][typed_column]
      if not exclude_order_column:
        typed_columns['order'] = 'NUMBER'
      for row in table['values']:
        for column in row:
          if not column in typed_columns:
            typed_columns[column] = 'TEXT'
     
      # CREATE TABLE statement
      column_names = list(typed_columns.keys())
      column_names.sort()
      create_table = f'CREATE TABLE _{table_name} ({ ",".join(map(lambda c: f"_{c} {typed_columns[c]}", column_names)) })'
      logger.debug(create_table)
      self.cursor.execute(create_table)

      # INSERT INTO
      row_index = 1
      for row in table['values']:
        if not exclude_order_column:
          row_modified = { 'order': row_index }
        else:
          row_modified = {}
        row_modified.update(row)
        columns = list(row_modified.keys())
        columns.sort()
        insert_into = f'INSERT INTO _{table_name} ({ ",".join(map(lambda c: f"_{c}", columns)) }) VALUES ({ ",".join(map(lambda c: "?", columns)) })'
        logger.debug(f'#{ row_index } - { insert_into } - { str(row_modified) }')
        self.cursor.execute(insert_into, list(map(lambda c: row_modified[c], columns)))
        row_index += 1

    logger.debug('Data object created.')

  def query (self, sql):
    return self.cursor.execute(sql)
