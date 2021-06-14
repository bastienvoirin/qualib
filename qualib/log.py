import traceback
from datetime import datetime, time

class Log():
    def initialize(self, timestamp, max_label_len=5):
        self.path = f'logs/{timestamp}.log'
        self.max_label_len = max_label_len
        
    def info(self, *args, **kwargs):
        self.log('info', *args, **kwargs)
        
    def debug(self, *args, **kwargs):
        self.log('debug', *args, **kwargs)
        
    def warn(self, *args, **kwargs):
        self.log('warn', *args, **kwargs)
        
    def error(self, *args, **kwargs):
        self.log('error', *args, **kwargs)
        
    def exc(self):
        self.error(traceback.format_exc().splitlines())
        
    def log(self, label, *args, **kwargs):
        if not args:
            return
        
        lines = []
        if isinstance(args[0], str):
            lines = list(args)    # self.log(*lines) variant
        else:
            lines = list(args[0]) # self.log(lines) variant
            
        assert hasattr(self, 'path') and hasattr(self, 'max_label_len'), 'Log() instances must be initialized'
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
        pre = f'[{now}] [{label.upper()}]' + ' '*(self.max_label_len - len(label))
        
        with open(self.path, 'a') as f:
            f.write(f'{pre} {lines.pop(0)}\n')
            for line in lines:
                f.write(f'{" "*len(pre)} {line}\n')
                
    def json(self, obj):
        return json.dumps(obj, indent=2).splitlines()