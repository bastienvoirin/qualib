import importlib

def load_(log, *args, **kwargs):
    log.info(f'Loading')
    try:
        pass
    except:
        log.error(f'Unable to load')
        log.exc()
        raise

def load_calibration_scheme(log, path):
    log.info(f'Loading calibration sequence expected at "{path}"')
    try:
        with open(path) as f:
            seq = f.read()
            return eval(seq), seq # calibration_scheme.py should be a Python list
    except:
        log.error(f'Unable to load or evaluate "{path}"')
        log.exc()
        raise
    
def load_exopy_template(log, calib):
    path = f'calibrations/{calib}/{calib}_template.meas.ini'
    log.info(f'Loading Exopy measurements template "{path}"')
    try:
        with open(path) as f:
            return f.read()
    except:
        log.error(f'Unable to load {path}')
        log.exc()
        raise
    
def load_assumptions(log):
    log.info(f'Loading "assumptions.py"')
    try:
        with open('assumptions.py') as f:
            return eval(f.read()) # assumptions.py should be a Python dict
    except:
        log.error('Unable to load or evaluate "assumptions.py"')
        log.exc()
        raise

def load_utils(log, calib):
    path = f'calibrations.{calib}.{calib}_utils'
    log.info(f'Importing Calibration class from "{path}"')
    try:
        module = importlib.import_module(path)
        return getattr(module, 'Calibration')
    except:
        log.error(f'Unable to import Calibration class from calibrations.{calib}.{calib}_utils')
        log.exc()
        raise