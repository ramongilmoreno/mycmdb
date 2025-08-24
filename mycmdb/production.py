import logging
from jinja2 import Template
import xml.etree.ElementTree as ET
from markdown_it import MarkdownIt

logger = logging.getLogger(__name__)

class Production:
  def __init__ (self, configuration, parameters = {}):
    logger.debug('Creating Production object...')
    self.parameters = parameters
    # Make sure self.parameters is not None, even if provided as None.
    if self.parameters == None:
      self.parameters = {}
    self.configuration = configuration
    self.additional = self.parameters.get('additional')
    if self.additional == None:
      self.additional = {}
    logger.debug('Production object created')

  def jinjaContext (self):
    return self.additional | { 'configuration': self.configuration }

  def produce_contents (self, template_contents, parameters = {}):
    jinja_template = Template(template_contents)
    return jinja_template.render(parameters | self.jinjaContext())

  def produce (self):
    logger.info('Start producing templates...')
    wrapper_template_contents = self.configuration.filesystem.wrapper_template_contents()
    if wrapper_template_contents:
      wrapper_template_contents = Template(wrapper_template_contents)
    for template in self.configuration.filesystem.production_templates():
      logger.info(f'Producing template {template.name}...')
      result = self.produce_contents(template.contents)
      if wrapper_template_contents:
        result = wrapper_template_contents.render(self.jinjaContext() | { 'body': result })
      transformation = self.parameters.get('transformation') or (lambda production, current_result, current_parameters: (current_result, current_parameters))
      r = transformation(self, result, {} | self.parameters)
      (self.configuration.filesystem.build_dir / template.name).write_text(r[0], encoding = 'utf8')
    logger.info('Finished producing templates.')

