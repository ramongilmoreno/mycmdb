import logging
logger = logging.getLogger(__name__)

from . import filesystem

from jinja2 import Template
import xml.etree.ElementTree as ET
import re

table_template = Template('''<table>
<thead>
<tr>
{% for column in columns -%}<th>{{ column }}</th>{% endfor %}
</tr>
</thead>
<tbody>
{% for row in rows -%}
<tr>
{% for field in row %}<td>{{ field }}</td>{% endfor %}
</tr>
{% endfor -%}
</tbody>
</table>''')

class Utils:
  def __init__ (self, configuration, parameters = {}):
    self.configuration = configuration
    self.parameters = parameters

  def render_query (self, columns, query, parameters = {}):
    context = {
      "columns": columns,
      "rows": self.configuration.data.query(query)
    }
    raw = table_template.render(context)

    # Do not merge rows if stated
    if parameters.get('do_not_merge_rows') == True:
      return raw

    # Default behaviour is to merge rows...
    xml = ET.fromstring(raw)
    columns = [i for i in xml.findall('./thead/tr/th')]
    rows = [i for i in xml.findall('./tbody/tr')]

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

