import logging
logger = logging.getLogger(__name__)
from . import filesystem
import xml.etree.ElementTree as ET
import re
import base64
import math

class HtmlUtils:
  def __init__ (self, configuration, parameters = {}):
    self.configuration = configuration
    self.parameters = parameters

  #
  # Format encoded in columns names:
  #
  # Column Name => Center aligned column with no particular CSS class
  # <Column Name[class1 class2] => Left aligned column with class1 and class2 CSS classes
  # ColumnName[class1]> => Right aligned column with class1 CSS class
  #
  # See render_query_ex_classes
  #
  # The "_ex" suffix naming choice comes from the "Extended" functions with the
  # same name that were introduced in Win32 API to enhance previous Win3x
  # simpler versions of the same functions.
  #
  def render_query_ex (self, columns_format_encoded, query, parameters = {}):
    def c (column):
      # Decide text alignment
      if column.startswith('<'):
        classes = [ 'render_query_ex_class_left' ]
        column = column[1:]
      elif column.endswith('>'):
        column = column[:1]
        classes = [ 'render_query_ex_class_right' ]
      else:
        classes = [ 'render_query_ex_class_center' ]
      # Find out classes
      groups = re.compile('^([^\[]+)(\[.*\])*$').match(column)
      column = groups.group(1)
      more_classes = groups.group(2)
      if more_classes != None:
        classes.extend(more_classes[1:-1].split(','))
      return {
        "name": column,
        "header_classes": classes,
        "classes": classes
      }
    return self.render_query(list(map(c, columns_format_encoded)), query, parameters) 

  def render_query_ex_classes (self):
    return '\n'.join(list(map(lambda x: f'.render_query_ex_class_{x} {{ text-align: {x}; }}', ['left', 'center', 'right'])))

  def render_query_no_columns (self, query, parameters = {}):
    # Run the query once and obtain columns
    # https://stackoverflow.com/a/7831685
    columns = list(map(lambda x: x[0], self.configuration.data.query(query).description))
    return self.render_query(columns, query, parameters)

  def render_query (self, columns, query, parameters = {}):
    table = ET.Element('table')
    thead = ET.SubElement(table, 'thead')
    tr = ET.SubElement(thead, 'tr')
    for column in columns:
      th = ET.SubElement(tr, 'th')
      if isinstance(column, dict):
        th.text = column['name']
        classes = set()
        if 'header_classes' in column:
          classes.update(column['header_classes'])
        if len(classes) > 0:
          th.set('class', ' '.join(classes))
      elif isinstance(column, str):
        th.text = column
      else:
        logger.error(f'Unknown column {str(column)}')
    tbody = ET.SubElement(table, 'tbody')
    for row in self.configuration.data.query(query):
      tr = ET.SubElement(tbody, 'tr')
      for field in enumerate(row):
        td = ET.SubElement(tr, 'td')
        td.text = str(field[1])
        classes = set()
        if 'classes' in columns[field[0]]:
          classes.update(columns[field[0]]['classes'])
        if 'function' in columns[field[0]]:
          classes.update(columns[field[0]]['function'](field[1], row) or [])
        if len(classes) > 0:
          td.set('class', ' '.join(classes))

    # Do not merge rows if stated
    flag = 'do_not_merge_rows'
    if parameters.get(flag) == True:
      table.set(flag, 'true')
    return ET.tostring(table, encoding = 'unicode', xml_declaration = False)

  def include_html (self, template, parameters = {}):
    template_contents = (self.configuration.filesystem.templates_dir / f'{template}.{filesystem.Template.extension}').read_text(encoding = 'utf8')
    raw = self.configuration.production.produce_contents(template_contents, parameters)
    h1_to_h = parameters['h1_to_h']
    if h1_to_h == None:
      return raw

    # Shift <hX> tags
    h1_to_h = int(h1_to_h)
    xml = ET.fromstring('<tag>' + raw + '</tag>')
    for i in reversed(range(6)):
      new_tag = f'h{min(6, i + h1_to_h - 1)}'
      for tag in xml.findall(f'.//h{i}'):
        tag.tag = new_tag
    return re.sub(r'^<tag>', '', re.sub(r'</tag>$', '', ET.tostring(xml, encoding = 'unicode', xml_declaration = False)))

  def include (self, template, parameters = {}):
    template_contents = (self.configuration.filesystem.templates_dir / f'{template}.{filesystem.Template.extension}').read_text(encoding = 'utf8')
    return self.configuration.production.produce_contents(template_contents, parameters)

  def static_base64 (self, resource_name, mime_type):
    data = self.configuration.filesystem.static_resource(resource_name)
    data = base64.b64encode(data)
    data = data.decode('utf-8')
    return f'data:{mime_type};base64,{data}'

  def paper_AX_sizes (self, custom_prefix = '_'):
    # https://tomroelandts.com/articles/how-is-the-size-of-a4-paper-determined#:~:text=The%20dimensions%20of%20the%20smaller,×%20297%20mm%20for%20A4.
    # A0 is the area of 1 square meter
    width = int(1000 / 2 ** (1 / 4) + 0.5)
    height = int(1000 * 2 ** (1 / 4) + 0.5)
    sizes = []
    for i in range(11):
      # print('A' + str(i), '=', width, 'x', height, 'mm')
      sizes.append((f'A{str(i)}', width, height))
      width, height = height, width
      width //= 2
    # https://dev.to/turbaszek/flat-map-in-python-3g98
    flat_map = lambda f, xs: [y for ys in xs for y in f(ys)]
    # For each A* paper size define -portrait and -landscape orientation
    sizes = flat_map(lambda s: [(s[0] + '-portrait', s[1], s[2]), (s[0] + '-landscape', s[2], s[1])], sizes)
    # For each orientation, define lines for @page <size and orientation> { ... } with dimensions, and a div.<size and orientation> CSS rule
    return '\n'.join(list(flat_map(lambda s: [f'@page {custom_prefix}page-size-{s[0]} {{ size: {s[1]}mm {s[2]}mm; margin: 12mm; }}', f'div.{custom_prefix}page-size-{s[0]} {{ page: {custom_prefix}page-size-{s[0]}; }}'], sizes)))

  def paper_AX_div_open (self, aX_size, portrait_orientation = True, custom_prefix = '_'):
    return f'<div paper_orientation="{custom_prefix}page-size-{aX_size}-' + ('portrait' if portrait_orientation else 'landscape') + '">'

  def paper_AX_div_close (self):
    return '</div>'

