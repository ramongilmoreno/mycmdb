import logging

logger = logging.getLogger(__name__)

class Production:
  def __init__ (self, parameters, filesystem, data):
    logger.debug('Creating Production object...')
    self.raw_parameters = parameters
    self.filesystem = filesystem
    self.data = data
    logger.debug('Production object created')

  def produce (self):
    for template in self.filesystem.production_templates():
      logger.info(f'Producing template {template.name}...')
    logger.info('Finished producing templates.')

