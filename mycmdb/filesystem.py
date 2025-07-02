#
# Ensures fileystem is OK for CMDB production
#

import logging
logger = logging.getLogger(__name__)

def default_dir (parameters, default, base):
  dir = parameters.get(default)
  if dir == None:
    dir = base / default
  return dir

def exists_dir (parameters, default, base):
  dir = default_dir(parameters, default, base)
  if not dir.is_dir():
    error = f'Mandatory directory for {default} configured as {dir} does not exists'
    raise AttributeError(error)
  return dir  

class Template:
  def __init__ (self, name, meta, contents):
    self.name = name
    self.meta = {} | meta
    self.contents = contents

class Filesystem:
  def __init__ (self, parameters):
    logger.debug('Creating Filesystem object...')
    self.raw_parameters = parameters

    self.base = parameters['base']
    logger.debug(f'Base directory at {self.base}')

    self.build_dir = exists_dir(parameters, 'build', self.base)
    self.templates_dir = exists_dir(parameters, 'templates', self.base)

    logger.debug('Filesystem object created.')

  def delayed_static_dir (self):
    if not self.static_dir:
      self.static_dir = default_dir(parameters['static'], 'static', self.base)
    return self.static_dir

  def production_templates (self):
    extension = '.jinja'
    def t (path):
      return Template(str(path)[len(str(self.templates_dir)) + 1:-len(extension)], {}, path.read_text(encoding = 'utf8'))
    return list(map(t, self.templates_dir.glob(f'*{extension}')))

