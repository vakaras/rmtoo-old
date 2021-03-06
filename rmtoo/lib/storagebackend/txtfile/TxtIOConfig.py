#
# rmtoo 
#   Free and Open Source Requirements Management Tool
#
# Text IO Configuration
#  This holds the configuration for the TxtIO class
#
# (c) 2011 by flonatel
#
# For licencing details see COPYING
#

from rmtoo.lib.RMTException import RMTException

class TxtIOConfig:

    def __init__(self, config=None):
        self.init_default()
        if config!=None:
            self.init_overwrite(config)

    def init_default(self):
        self.max_line_length = 80

    def set_max_line_length(self, n):
        self.max_line_length = n

    def get_max_line_length(self):
        return self.max_line_length
        
    def init_overwrite(self, ioconfig):
        if "max_line_length" in ioconfig:
            v = ioconfig["max_line_length"]
            if not isinstance(v, int):
                raise RMTException(
                    71, "txtioconfig['max_line_length'] is "
                    "not an integer - wich should be; type is [%s]"
                    % type(v).__name__)
            if v<0:
                raise RMTException(72, "txtioconfig['max_line_length'] is "
                                   "negative [%s]" % v)

            self.set_max_line_length(int(v))
        
