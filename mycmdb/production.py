import logging
from jinja2 import Template

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

  def produce (self):
    logger.info('Start producing templates...')
    for template in self.configuration.filesystem.production_templates():
      if template.name.startswith('_'):
        continue
      logger.info(f'Producing template {template.name}...')
      result = self.produce_contents(template.contents)
      (self.configuration.filesystem.build_dir / template.name).write_text(result, encoding = 'utf8')
    logger.info('Finished producing templates.')

