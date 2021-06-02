import sys
import subprocess
import importlib
import h5py
import time
import re

class Qualib:
    """
    Wrapper supclass
    """
    def __init__(self):
        return
    
    def run(self, calib_id, calib_name, substitutions):
        """
        Run a single calibration with given assumptions and Exopy template
        """
        print('Starting a "{}" calibration with {} substitution(s):\n    {}'.format(
            calib_name,
            len(substitutions.keys()),
            '\n    '.join(map(lambda kv: '{} => {}'.format(kv[0],kv[1]), substitutions.items()))
        ))
        
        try:
            Calibration = load_utils(calib_name)
            print('✓ Successfully loaded {0}_utils.py'.format(calib_name))
            
            assumptions = Assumptions.load(calib_name)
            print('✓ Successfully loaded assumptions for "{}"'.format(calib_name))
            
            exopy_templ = ExopyTemplate.load(calib_name)
            print('✓ Successfully loaded Exopy template for "{0}"\n  Generating {0}.meas.ini file...'.format(calib_name))
            calibration = Calibration(exopy_templ, assumptions, calib_id, calib_name, substitutions)
            keys = calibration.keys
            
            print('✓ Successfully saved {0}.meas.ini in calibrations/{0}'.format(calib_name))
            print('✓ Starting a "{}" calibration...'.format(calib_name))
            ini_path = '../qualib/calibrations/{0}/{0}.meas.ini'.format(calib_name)
            subprocess.run(['python', '-m', 'exopy', '-s', '-x', ini_path], shell=True)
            calibration.analyze('{}/{:03d}_{}.h5'.format(assumptions['default_path'], calibration.calib_id, calibration.calib_name))
            result = calibration.result
            print('Result of "{}" calibration: {}'.format(calib_name, result))
        except:
            print('  An error occurred while processing "{}" calibration:\n    {}\n\n{}\n'.format(calib_name, sys.exc_info()[1], '#'*70))
            raise
        return
    
    def run_all(self):
        """
        Run a calibration scheme with given Exopy templates, assumptions and utils
        """
        if len(sys.argv):
            calib_id = 0
            path = sys.argv[1] # path to the calibration scheme
            calib_scheme = CalibrationScheme.load(path)
            for calib in calib_scheme:
                if 'substitutions' in calib:
                    for substitutions in calib['substitutions']:
                        calib_id += 1
                        self.run(calib_id, calib['name'], substitutions)
                        print()
                else:
                    calib_id += 1
                    self.run(calib_id, calib['name'], {})
                    print()
        return
    
class CalibrationScheme:
    """
    Load a sequence of calibrations (a list of calibration names in a .txt file)
    """
    def load(path):
        calib_scheme = []
        with open(path) as f:
            return eval(f.read())
    
class ExopyTemplate:
    """
    Load an Exopy template defining a specific calibration
    """
    def load(calib):
        with open('calibrations/{}/{}_template.meas.ini'.format(calib, calib)) as f:
            return f.read()
    
class Assumptions:
    """
    Parse a dict of assumptions
    """
    def load(calib):
        with open('assumptions.py'.format(calib, calib)) as f:
            return eval(f.read())

def load_utils(calib):
    """
    Import utils module dynamically
    """
    module = importlib.import_module('calibrations.{}.{}_utils'.format(calib, calib))
    return getattr(module, 'Calibration') # Calibration class from {calib_name}_utils.py
    
qualib = Qualib()
qualib.run_all()
