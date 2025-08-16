import logging
from jinja2 import Template
import xml.etree.ElementTree as ET
from markdown_it import MarkdownIt

logger = logging.getLogger(__name__)

#
# Compose transformations
#
def transformation_builder (*transformations):
  def composition (context, current_result, parameters):
    next_result = current_result
    next_parameters = parameters
    for t in transformations:
      r = t(context, next_result, next_parameters)
      next_result = r[0]
      next_parameters = r[1]
    return (next_result, next_parameters)
  return composition

#
# Custom transformations functions: receives a production object as context,
# the current object being processed and a set of parameters. Returns a tuple
# of the modified result -to pass to the next transformation function- and the
# modified parameters.
#

#
# Convert to XML with xml.etree.ElementTree
#
def to_xml (context, current_result, parameters):
  return (ET.fromstring(current_result), parameters)

#
# Page orientation: iterate the <div> elements with page orientation and decide
# which requires a section break based on current orientation setting
#
def page_orientation (context, current_xml, parameters):
  orientation_current = None
  to_insert = []
  for parent_element in current_xml.findall(".//div[@paper_orientation]/.."):
    # Parent element can only be obtained like this
    for element in parent_element.findall("./div[@paper_orientation]"):
      orientation_new = element.get('paper_orientation')
      del element.attrib['paper_orientation']
      orientation_before = orientation_current
      orientation_current = orientation_new
      if orientation_before == None:
        pass
      else:
        # Apply a page break and add a class
        element.set('class', orientation_current)
        index = list(parent_element.findall('*')).index(element)
        to_insert.append((parent_element, index))
        new_element_span = ET.Element('span')
        new_element_br = ET.Element('br')
        new_element_br.set('clear', 'all')
        new_element_br.set('style', 'mso-break-type:section-break')
        new_element_span.append(new_element_br)
        parent_element.insert(index, new_element_span)
  return (current_xml, parameters)

#
# Parse Markdown tags
#
def markdown_tags (context, current_xml, parameters):
  md = MarkdownIt()
  for parent_of_markdown in current_xml.findall('.//markdown/..'):
    # Results in reversed() to preserve indexes when replacing
    for markdown in reversed(parent_of_markdown.findall('markdown')):
      index = list(parent_of_markdown).index(markdown)
      new_section = ET.fromstring('<span>' + md.render(markdown.text) + '</span>')
      parent_of_markdown.insert(index, new_section)
      parent_of_markdown.remove(markdown)
  return (current_xml, parameters)

#
# Render XML as text again
#
def from_xml (context, current_xml, parameters):
  return (ET.tostring(current_xml, encoding = 'unicode', xml_declaration = False), parameters)

