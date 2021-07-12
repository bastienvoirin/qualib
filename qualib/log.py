from __future__ import annotations
import json
import traceback
from datetime import datetime, time
from typing import Union

class Log():
    """Logs timestamped and labeled informations ("info"), debug informations
    ("debug"), warnings ("warn"), errors ("error"), and/or custom content.
    
    Keyword arguments ``**kwargs`` are not supported yet, but may be added in
    future versions.
    """
    
    def initialize(self, timestamp: str, max_label_len: int = 5) -> Log:
        """
        Args:
            timestamp: Timestamp string
            max_label_len: Maximum label length in characters (e.g. ``5`` if the possible labels are ``DEBUG``, ``INFO``, ``WARN`` and ``ERROR``). Log entries (``prefix: message`` or ``message``) are aligned according to this constant: set ``max_label_len`` to ``0`` to disable log entries alignment.
            
        Returns:
            A logging object.
        """
        self.path = f'logs/{timestamp}.log'
        self.max_label_len = max_label_len
        return self
    
    def debug(self, prefix: str, *lines: str, **kwargs) -> Log:
        """Logs a debug message.
        
        Args:
            prefix: Optional log entry prefix (set ``prefix`` to ``""`` to log a message without a prefix).
            lines: Lines to log (1 argument each: use the unpack operator ``*`` to log a list of lines).
        
        Returns:
            ``self``
        """
        return self.log('debug', prefix, *lines, **kwargs)
    
    def info(self, prefix: str, *lines: str, **kwargs) -> Log:
        """Logs an information message.
        
        Args:
            prefix: Optional log entry prefix (set ``prefix`` to ``""`` to log a message without a prefix).
            lines: Lines to log (1 argument each: use the unpack operator ``*`` to log a list of lines).
        
        Returns:
            ``self``
        """
        return self.log('info', prefix, *lines, **kwargs)
        
    def warn(self, prefix: str, *lines: str, **kwargs) -> Log:
        """Logs a warning message.
        
        Args:
            prefix: Optional log entry prefix (set ``prefix`` to ``""`` to log a message without a prefix).
            lines: Lines to log (1 argument each: use the unpack operator ``*`` to log a list of lines).
        
        Returns:
            ``self``
        """
        return self.log('warn', prefix, *lines, **kwargs)
        
    def error(self, prefix: str, *lines: str, **kwargs) -> Log:
        """Logs an error message.
        
        Args:
            prefix: Optional log entry prefix (set ``prefix`` to ``""`` to log a message without a prefix).
            lines: Lines to log (1 argument each: use the unpack operator ``*`` to log a list of lines).
        
        Returns:
            ``self``
        """
        return self.log('error', prefix, *lines, **kwargs)
        
    def exc(self) -> Log:
        """Logs the current exception traceback as an error message.
        
        Returns:
            ``self``
        """
        return self.error(traceback.format_exc().splitlines())

    def log(self, label: str, prefix: str, *lines: str, **kwargs) -> Log:
        """Logs a message with given label and prefix.
        
        Args:
            label: Label of the log entry (e.g. ``warn``).
            prefix: Optional log entry prefix (set ``prefix`` to ``""`` to log a message without a prefix).
            lines: Lines to log (1 argument each: use the unpack operator ``*`` to log a list of lines).
            
        Returns:
            ``self``
        """
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
            
        Returns:
            Indented string representation of ``obj``.
        """
        return json.dumps(obj, indent=2, ensure_ascii=False).splitlines()