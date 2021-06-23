from __future__ import annotations
import importlib
from typing import Tuple
from .calibrations.CALIBRATION_NAME_utils import Calibration

def load_calibration_scheme(log, path: str) -> Tuple[list, str]:
    """
    Returns:
        Parsed calibration sequence, raw calibration sequence.
    """
    log.info(f'Loading calibration sequence "{path}"')
    try:
        with open(path, encoding='utf-8') as f:
            seq = f.read()
            return eval(seq), seq # calibration_scheme.py should be a Python list
    except:
        log.error(f'Unable to load or evaluate "{path}"')
        log.exc()
        raise
    
def load_assumptions(log) -> dict:
    """
    Returns:
        `dict`: Assumptions before any calibration.
    """
    log.info(f'Loading "assumptions.py"')
    try:
        with open('assumptions.py', encoding='utf-8') as f:
            return eval(f.read()) # assumptions.py should be a Python dict
    except:
        log.error('Unable to load or evaluate "assumptions.py"')
        log.exc()
        raise

def load_utils(log, name: str, prefix: str) -> Calibration:
    """
    Returns:
        Calibration class from ``CALIBRATION_NAME_utils.py``.
    """
    path = f'qualib.calibrations.{name}.{name}_utils'
    log.info(prefix, f'Importing Calibration class from "qualib/calibrations/{name}/{name}_utils.py"')
    try:
        module = importlib.import_module(path)
        return getattr(module, 'Calibration')
    except:
        log.error(f'Unable to import Calibration class from {path}')
        log.exc()
        raise
    
def load_exopy_template(log, name: str, prefix: str) -> str:
    """
    Returns:
        Contents of the Exopy template for a given calibration name.
    """
    path = f'qualib/calibrations/{name}/{name}_template.meas.ini'
    log.info(prefix, f'Loading Exopy measurements template "{path}"')
    try:
        with open(path, encoding='utf-8') as f:
            return f.read()
    except:
        log.error(f'Unable to load {path}')
        log.exc()
        raise