import logging
logger = logging.getLogger(__name__)
from . import filesystem
import xml.etree.ElementTree as ET
import re
import base64
import math

class Utils:
  def __init__ (self, configuration, parameters = {}):
    self.configuration = configuration
    self.parameters = parameters

  def render_query (self, columns, query, parameters = {}):
    table = ET.Element('table')
    thead = ET.SubElement(table, 'thead')
    tr = ET.SubElement(thead, 'tr')
    for column in columns:
      th = ET.SubElement(tr, 'th')
      if isinstance(column, dict):
        th.text = column['name']
      elif isinstance(column, str):
        th.text = column
      else:
        logger.error(f'Unknown column {str(column)}')
    tbody = ET.SubElement(table, 'tbody')
    for row in self.configuration.data.query(query):
      tr = ET.SubElement(tbody, 'tr')
      for field in enumerate(row):
        td = ET.SubElement(tr, 'td')
        td.text = field[1]
        classes = set()
        if 'classes' in columns[field[0]]:
          classes.update(columns[field[0]]['classes'])
        if 'function' in columns[field[0]]:
          classes.update(columns[field[0]]['function'](field[1], row) or [])
        if len(classes) > 0:
          td.set('class', ' '.join(classes))

    # Do not merge rows if stated
    if parameters.get('do_not_merge_rows') == True:
      return ET.tostring(table, encoding = 'unicode', xml_declaration = False)
    # Default behaviour is to merge rows...
    xml = table
    columns = [i for i in xml.findall('thead/tr/th')]
    rows = [i for i in xml.findall('tbody/tr')]

    # Reverse columns order, so td are deleted from the rightmost cells first
    # (deleting from left would cause td indexes to get shifted to the left)
    for i in reversed(range(len(columns))):
      logger.debug(f'Merging column { columns[i].text }')
      values = [row.findall('./td')[i] for row in rows]
      last_value = None
      last_value_count = 1
      for j in range(len(rows)):
        value = values[j]
        if (last_value == None) or (last_value.text != value.text):
          last_value = value
          last_value_count = 1
        else:
          last_value_count += 1
          last_value.attrib['rowspan'] = str(last_value_count)
          rows[j].remove(value)

    return ET.tostring(xml, encoding = 'unicode', xml_declaration = False)

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

