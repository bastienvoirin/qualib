import sys
import subprocess
import importlib
import h5py
import time
import re
from datetime import datetime
from calibrations.default import DefaultJupyterReport

class Qualib:
    """
    Wrapper supclass
    """
    def __init__(self):
        return
    
    def run(self, calib_id, calib_name, substitutions, report_filename):
        """
        Run a single calibration with given assumptions and Exopy template
        """
        print(f'Starting a "{calib_name}" calibration with {len(substitutions.keys())} substitution(s):')
        print(' '*4+'\n    '.join(map(lambda pair: f'{pair[0]} => {pair[1]}', substitutions.items())))
        
        try:
            # dynamically import Calibration from calibrations/{name}/{name}_utils.py
            Calibration, JupyterReport = load_utils(calib_name)
            print(f'✓ Successfully loaded {calib_name}_utils.py')
            
            # load assumptions.py
            assumptions = Assumptions.load(calib_name)
            print(f'✓ Successfully loaded assumptions for "{calib_name}"')
            
            # load calibrations/{name}/{name}_template.meas.ini
            exopy_templ = ExopyTemplate.load(calib_name)
            print(f'✓ Successfully loaded Exopy template for "{calib_name}"\n  Generating {calib_name}.meas.ini file...')
            
            # generate and save calibrations/{name}/{name}.meas.ini
            calibration = Calibration(exopy_templ, assumptions, calib_id, calib_name, substitutions)
            keys = calibration.keys
            print(f'✓ Successfully saved {calib_name}.meas.ini in calibrations/{calib_name}')
            
            # run 'python -m exopy -s -x ../qualib/calibrations/{name}/{name}.meas.ini'
            print(f'✓ Starting a "{calib_name}" calibration...')
            ini_path = f'../qualib/calibrations/{calib_name}/{calib_name}.meas.ini'
            subprocess.run(['python', '-m', 'exopy', '-s', '-x', ini_path], shell=True)
            
            # process the hdf5 output file
            # calibration.analyze(f'{assumptions["default_path"]}/{calibration.calib_id:03d}_{calibration.calib_name}.h5')
            result = {'a_rabi': 34}
            units = {'a_rabi': ''}
            calibration.result = result
            calibration.units = units
            result = calibration.result
            print(f'Result of "{calib_name}" calibration:\n{result}')
            print(calibration.report(substitutions, report_filename))
        except:
            print(f'  An error occurred while processing "{calib_name}" calibration:')
            print(f'    {sys.exc_info()[1]}\n\n{"#"*70}\n')
            raise # propagate the exception to show the stack trace and prevent the next calibration
        return
    
    def run_all(self):
        """
        Run a calibration scheme with given Exopy templates, assumptions and utils
        """
        now = datetime.now()
        timestamp = now.strftime('%y_%m_%d_%H%M%S')
        #report_filename = f'report_{timestamp}.ipynb'
        report_filename = 'report_temporary.ipynb'
        with open('report_template.ipynb', 'r') as f:
            with open('report_temporary.ipynb', 'w') as g:
                g.write(f.read())
        #global_report = DefaultJupyterReport()
        #global_report.generate(report_filename) # create blank .ipynb report
        if len(sys.argv):
            calib_id = 0
            path = sys.argv[1] # path to calibration_scheme.py
            calib_scheme = CalibrationScheme.load(path)
            for calib in calib_scheme:
                if 'substitutions' in calib:
                    for substitutions in calib['substitutions']:
                        calib_id += 1
                        self.run(calib_id, calib['name'], substitutions, report_filename)
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
            return eval(f.read()) # calibration_scheme.py should be a Python dict
    
class ExopyTemplate:
    """
    Load an Exopy template defining a specific calibration
    """
    def load(calib):
        with open(f'calibrations/{calib}/{calib}_template.meas.ini') as f:
            return f.read()
    
class Assumptions:
    """
    Parse a dict of assumptions
    """
    def load(calib):
        with open('assumptions.py') as f:
            return eval(f.read()) # assumptions.py should be a Python list

def load_utils(calib):
    """
    Import utils module dynamically
    """
    module = importlib.import_module(f'calibrations.{calib}.{calib}_utils')
    Calibration = getattr(module, 'Calibration') # Calibration class from {calib_name}_utils.py
    JupyterReport = getattr(module, 'JupyterReport') # JupyterReport class from {calib_name}_utils.py
    return Calibration, JupyterReport
    
qualib = Qualib()
qualib.run_all()
