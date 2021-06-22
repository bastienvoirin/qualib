import json
import traceback
from datetime import datetime, time

class Log():
    """Logs timestamped and labeled informations ("info"), debug informations ("debug"), warnings ("warn"), errors ("error"), and/or custom content.
    
    Keyword arguments ``**kwargs`` are not supported yet, but may be added in future versions.
    """
    
    def initialize(self, timestamp, max_label_len=5):
        """Sets ``self.path`` and ``self.max_label_len``.
        
        Args:
            timestamp (str): A user-defined timestamp.
            max_label_len (int): Defaults to `5`.
        """
        self.path = f'logs/{timestamp}.log'
        self.max_label_len = max_label_len
        return self
        
    def info(self, prefix, *args, **kwargs):
        """Calls ``log('info', *args, **kwargs)``.
        
        """
        self.log('info', prefix, *args, **kwargs)
        return self
        
    def debug(self, prefix, *args, **kwargs):
        """Calls ``log('debug', *args, **kwargs)``.
        
        """
        self.log('debug', prefix, *args, **kwargs)
        return self
        
    def warn(self, prefix, *args, **kwargs):
        """Calls ``log('warn', *args, **kwargs)``.
        
        """
        self.log('warn', prefix, *args, **kwargs)
        return self
        
    def error(self, prefix, *args, **kwargs):
        """Calls ``log('error', *args, **kwargs)``.
        
        """
        self.log('error', prefix, *args, **kwargs)
        return self
        
    def exc(self):
        """Logs the current exception traceback with an ``[ERROR]`` label.
        
        """
        self.error(traceback.format_exc().splitlines())
        return self

    def log(self, label, prefix, *args, **kwargs):
        """Logs its arguments.
        
        Multiples lines may be passed to this method
    
            * As a list: ``log(label, lines)``, `e.g.` ``log('info', [line1, line2, line3])``
            * As multiple arguments: ``log(label, *lines)``, `e.g.` ``log('info', line1, line2, line3)``.
        """
        if not args:
            return
        
        lines = []
        if isinstance(args[0], str):
            lines = list(args)    # self.log(*lines) variant
        else:
            lines = list(args[0]) # self.log(lines) variant
            
        assert hasattr(self, 'path') and hasattr(self, 'max_label_len'), 'Log() instances must be initialized'
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
        pre = f'[{now}] [{label.upper()}]' + ' '*(self.max_label_len - len(label)) + f'{" "+prefix if prefix else ""}'
        
        with open(self.path, 'a', encoding='utf-8') as f:
            for line in lines:
                f.write(f'{pre} {line}\n')
                
        return self
                
    def json(self, obj):
        """Returns an indented string representation of an object.
        
        Args:
            obj (`list` or `dict`): Object to stringify.
        """
        return json.dumps(obj, indent=2, ensure_ascii=False).splitlines()