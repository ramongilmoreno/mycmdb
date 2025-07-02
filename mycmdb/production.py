import logging
from jinja2 import Template

logger = logging.getLogger(__name__)

class Production:
  def __init__ (self, parameters, configuration):
    logger.debug('Creating Production object...')
    self.parameters = {} if not parameters else parameters
    self.configuration = configuration
    logger.debug('Production object created')

  def jinjaContext (self):
    return {
      'configuration': self.configuration,
      'additional': self.parameters.get('additional')
    }

  def produce (self):
    for template in self.configuration.filesystem.production_templates():
      logger.info(f'Producing template {template.name}...')
      jinja_template = Template(template.contents)
      result = jinja_template.render(self.jinjaContext())
      (self.configuration.filesystem.build_dir / template.name).write_text(result, encoding = 'utf8')
    logger.info('Finished producing templates.')

