#
# Main configuration tool
#

import logging
logger = logging.getLogger(__name__)

from . import filesystem
from . import data
from . import production
from . import utils

class Configuration:
  def __init__ (self, parameters):
    self.parameters = parameters
    if parameters.get('skip_initialization_in_init') == True:
      logger.debug('Delayed initialization. Need to call init() before using this object.')
    else:
      self.init()

  def init (self):
    # Check initialization is OK
    self.init_filesystem()
    self.init_data()
    self.init_production()
    self.init_utils()
    self.initialized = True

  def init_filesystem (self):
    parameters = self.parameters.get("filesystem")
    if parameters == None:
      error = 'Missing "fileystem" attribute in configuration parameters'
      logger.error(error)
      raise AttributeError(error)
    self.filesystem = filesystem.Filesystem(self, parameters)
    logger.debug('Fileystem initialization completed')

  def init_data (self):
    parameters = self.parameters.get("data")
    if parameters == None:
      error = 'Missing "data" attribute in configuration parameters'
      logger.error(error)
      raise AttributeError(error)
    self.data = data.Data(self, parameters)
    logger.debug('Data initialization completed')

  def init_production (self):
    parameters = self.parameters.get("production")
    self.production = production.Production(self, parameters)

  def init_utils (self):
    parameters = self.parameters.get("utils")
    self.utils = utils.Utils(self, parameters)

  def run (self):
    if not self.initialized:
      e = 'Configuration not yet initialized. Make sure Configuration.init() is called'
      logger.error(e)
      raise RuntimeError(e)
    self.production.produce()

def configure (parameters):
  return Configuration(parameters)

