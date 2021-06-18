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
    """

    :return:
    :rtype: dict, str
    :raise:
    """
    log.info(f'Loading calibration sequence "{path}"')
    try:
        with open(path, encoding='utf8') as f:
            seq = f.read()
            return eval(seq), seq # calibration_scheme.py should be a Python list
    except:
        log.error(f'Unable to load or evaluate "{path}"')
        log.exc()
        raise
    
def load_exopy_template(log, calib, sub):
    """

    :return: Contents of the Exopy template for a given calibration name
    :rtype: str
    :raise:
    """
    path = f'qualib/calibrations/{calib}/{calib}_template.meas.ini'
    log.info(f'{calib}{"_"+sub if sub else ""}: Loading Exopy measurements template "{path}"')
    try:
        with open(path, encoding='utf8') as f:
            return f.read()
    except:
        log.error(f'Unable to load {path}')
        log.exc()
        raise
    
def load_assumptions(log):
    """

    :return: Assumptions before any calibration
    :rtype: dict
    :raise:
    """
    log.info(f'Loading "assumptions.py"')
    try:
        with open('assumptions.py', encoding='utf8') as f:
            return eval(f.read()) # assumptions.py should be a Python dict
    except:
        log.error('Unable to load or evaluate "assumptions.py"')
        log.exc()
        raise

def load_utils(log, calib, sub):
    """

    :return: Calibration class from `CALIBRATION_NAME_utils.py`
    :rtype: Calibration
    :raise:
    """
    path = f'qualib.calibrations.{calib}.{calib}_utils'
    log.info(f'{calib}{sub}: Importing Calibration class from "qualib/calibrations/{calib}/{calib}_utils.py"')
    try:
        module = importlib.import_module(path)
        return getattr(module, 'Calibration')
    except:
        log.error(f'Unable to import Calibration class from {path}')
        log.exc()
        raise