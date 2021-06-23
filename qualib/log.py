from __future__ import annotations
import json
import traceback
from datetime import datetime, time
from typing import Union

class Log():
    """
    Logs timestamped and labeled informations ("info"), debug informations
    ("debug"), warnings ("warn"), errors ("error"), and/or custom content.
    
    Keyword arguments ``**kwargs`` are not supported yet, but may be added in
    future versions.
    """
    
    def initialize(self, timestamp: str, max_label_len: int = 5) -> Log:
        self.path = f'logs/{timestamp}.log'
        self.max_label_len = max_label_len
        return self
        
    def info(self, prefix: str, *lines: str, **kwargs) -> Log:
        return self.log('info', prefix, *lines, **kwargs)
        
    def debug(self, prefix: str, *lines: str, **kwargs) -> Log:
        return self.log('debug', prefix, *lines, **kwargs)
        
    def warn(self, prefix: str, *lines: str, **kwargs) -> Log:
        return self.log('warn', prefix, *lines, **kwargs)
        
    def error(self, prefix: str, *lines: str, **kwargs) -> Log:
        return self.log('error', prefix, *lines, **kwargs)
        
    def exc(self) -> Log:
        return self.error(traceback.format_exc().splitlines())

    def log(self, label: str, prefix: str, *lines: str, **kwargs) -> Log:
        if not lines:
            return
        
        assert hasattr(self, 'path') and hasattr(self, 'max_label_len'),\
               'Log() instances must be initialized'
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
        pre = ''.join([f'[{now}] [{label.upper()}]',
                       ' '*(self.max_label_len - len(label)),
                       f'{" "+prefix if prefix else ""}'])
        
        with open(self.path, 'a', encoding='utf-8') as f:
            for line in lines:
                f.write(f'{pre} {line}\n')
        return self
                
    def json(self, obj: list|dict) -> str:
        """Returns an indented string representation of an object.
        
        Args:
            obj: Object to stringify.
        """
        return json.dumps(obj, indent=2, ensure_ascii=False).splitlines()