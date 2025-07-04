from jinja2 import Template
from . import filesystem

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
    return table_template.render(context)

  def include (self, template, parameters = {}):
    template_contents = (self.configuration.filesystem.templates_dir / f'{template}.{filesystem.Template.extension}').read_text(encoding = 'utf8')
    return self.configuration.production.produce_contents(template_contents, parameters)

