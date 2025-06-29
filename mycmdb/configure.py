#
# Main configuration tool
#

import logging
logger = logging.getLogger(__name__)

from . import filesystem
from . import data
from . import production

class Configuration:
  def __init__ (self, parameters):
    self.original_parameters = parameters
    if parameters.get('skip_initialization_in_init') == True:
      logger.debug('Delayed initialization. Need to call init() before using this object.')
    else:
      self.init()

  def init (self):
    # Check initialization is OK
    self.init_filesystem()
    self.init_data()
    self.init_production()
    self.initialized = True

  def init_filesystem (self):
    parameters = self.original_parameters.get("filesystem")
    if parameters == None:
      error = 'Missing "fileystem" attribute in configuration parameters'
      logger.error(error)
      raise AttributeError(error)
    self.filesystem = filesystem.Filesystem(parameters)
    logger.debug('Fileystem initialization completed')

  def init_data (self):
    parameters = self.original_parameters.get("data")
    if parameters == None:
      error = 'Missing "data" attribute in configuration parameters'
      logger.error(error)
      raise AttributeError(error)
    self.data = data.Data(parameters)
    logger.debug('Data initialization completed')

  def init_production (self):
    parameters = self.original_parameters.get("production")
    self.production = production.Production(parameters, self.filesystem, self.data)

  def run (self):
    if not self.initialized:
      e = 'Configuration not yet initialized. Make sure Configuration.init() is called'
      logger.error(e)
      raise RuntimeError(e)
    self.production.produce()

def configure (parameters):
  return Configuration(parameters)

