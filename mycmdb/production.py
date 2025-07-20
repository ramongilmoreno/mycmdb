import logging
from jinja2 import Template
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class Production:
  def __init__ (self, configuration, parameters = {}):
    logger.debug('Creating Production object...')
    self.parameters = parameters
    # Make sure self.parameters is not None, even if provided as None.
    if self.parameters == None:
      self.parameters = {}
    self.configuration = configuration
    logger.debug('Production object created')

  def jinjaContext (self):
    return {
      'configuration': self.configuration,
      'additional': self.parameters.get('additional')
    }

  def produce_contents (self, template_contents, parameters = {}):
    jinja_template = Template(template_contents)
    return jinja_template.render(self.jinjaContext() | parameters)

  def produce (self, parameters = {}):
    logger.info('Start producing templates...')
    wrapper_template_contents = self.configuration.filesystem.wrapper_template_contents()
    if wrapper_template_contents:
      wrapper_template_contents = Template(wrapper_template_contents)
    for template in self.configuration.filesystem.production_templates():
      logger.info(f'Producing template {template.name}...')
      result = self.produce_contents(template.contents)
      if wrapper_template_contents:
        result = wrapper_template_contents.render(self.jinjaContext() | parameters | { 'body': result })
      # Page orientation: iterate the <div> elements with page orientation and
      # decide which requires a section break based on current orientation
      # setting
      if parameters.get('do_not_perform_page_orientation') == True:
        pass
      else:
        # Load as XML
        logger.debug('Processing page orientation changes...')
        xml = ET.fromstring('<X>' + result + '</X>')
        orientation_current = None
        to_insert = []
        for parent_element in xml.findall(".//div[@paper_orientation]/.."):
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
        result = ET.tostring(xml[0], encoding = 'unicode', xml_declaration = False)
      (self.configuration.filesystem.build_dir / template.name).write_text(result, encoding = 'utf8')
    logger.info('Finished producing templates.')

