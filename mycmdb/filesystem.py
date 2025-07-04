#
# Ensures fileystem is OK for CMDB production
#

import logging
logger = logging.getLogger(__name__)

import re

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
  extension = 'jinja'
  def __init__ (self, name, meta, contents):
    self.name = name
    self.meta = {} | meta
    self.contents = contents

class Filesystem:
  def __init__ (self, configuration, parameters):
    logger.debug('Creating Filesystem object...')
    self.configuration = configuration
    self.parameters = {} if not parameters else parameters
    self.wrapper_template = self.parameters.get('wrapper_template')

    self.base = parameters['base']
    logger.debug(f'Base directory at {self.base}')

    self.build_dir = exists_dir(parameters, 'build', self.base)
    self.templates_dir = exists_dir(parameters, 'templates', self.base)

    logger.debug('Filesystem object created.')

  def delayed_static_dir (self):
    if not self.static_dir:
      self.static_dir = default_dir(parameters['static'], 'static', self.base)
    return self.static_dir

  def wrapper_template_contents (self):
    if self.wrapper_template:
      return self.wrapper_template
    else:
      # Try to load _wrapper.jinja
      wrapper_path = self.templates_dir / f'_wrapper.{Template.extension}'
      if wrapper_path.exists():
        self.wrapper_template = wrapper_path.read_text(encoding = 'utf8')
    return self.wrapper_template

  def production_templates (self):
    def t (path):
      return Template(str(path)[len(str(self.templates_dir)) + 1:-len(f'.{Template.extension}')], {}, path.read_text(encoding = 'utf8'))
    def not_underscore (path):
      return not re.match(r'.*_[^/]*$', str(path))
    return list(map(t, filter(not_underscore, self.templates_dir.glob(f'*.{Template.extension}'))))

