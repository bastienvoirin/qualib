import os
from pathlib import Path
import sys
import subprocess
import importlib
from datetime import datetime
from calibrations.default import DefaultJupyterReport

class Qualib:
    """
    Wrapper supclass
    """
    def run(self, calib_id, calib_name, sub_name, sub_repl, report_filename, timestamp, assumptions):
        """
        Run a single calibration with given assumptions and Exopy template
        """
        print(f'Starting a "{calib_name}{f"_{sub_name}" if sub_name else ""}" calibration with {len(sub_repl.keys())} substitution(s):')
        print(' '*4+'\n    '.join(map(lambda pair: f'{pair[0]} => {pair[1]}', sub_repl.items())))
        
        try:
            # Dynamically import Calibration from calibrations/{name}/{name}_utils.py
            Calibration, JupyterReport = load_utils(calib_name)
            print(f'✓ Successfully loaded {calib_name}_utils.py')
            
            # Load calibrations/{name}/{name}_template.meas.ini
            exopy_templ = load_exopy_template(calib_name)
            print(f'✓ Successfully loaded Exopy template for "{calib_name}"\n  Generating {calib_name}.meas.ini file...')
            
            # Generate and save calibrations/{name}/{name}.meas.ini
            calibration = Calibration(exopy_templ, assumptions, calib_id, calib_name, sub_name, sub_repl, timestamp)
            keys = calibration.keys
            print(f'✓ Successfully saved {calib_name}.meas.ini in calibrations/{calib_name}')
            
            # Run 'python -m exopy -s -x ../qualib/calibrations/{name}/{name}.meas.ini'
            print(f'✓ Starting a "{calib_name}{f"_{sub_name}" if sub_name else ""}" calibration...\n')
            ini_path = str(Path(os.path.realpath(__file__)).parent / f'calibrations/{calib_name}/{calib_name}.meas.ini')
            subprocess.run(['python', '-m', 'exopy', '-s', '-x', ini_path], shell=True)
            print()
            
            # Process the hdf5 output file and report the result(s)
            calibration.process(calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions)
        except:
            print(f'  An error occurred while processing "{calib_name}" calibration:')
            print(f'    {sys.exc_info()[1]}\n\n{"#"*70}\n')
            raise # Propagate the exception to show the stack trace and prevent the next calibration
        return
    
    def run_all(self):
        """
        Run a calibration scheme with given Exopy templates, assumptions and utils
        """
        assert len(sys.argv) > 1, 'Missing calibration scheme\n\npython qualib.py calibration_scheme.py'
        calib_id = 0
        calib_scheme = load_calibration_scheme(sys.argv[1])
        
        now = datetime.now()
        timestamp = now.strftime('%y_%m_%d_%H%M%S')
        report_filename = f'report_{timestamp}.ipynb'
        report = DefaultJupyterReport()
        print(f'\n\nStarting calibration sequence => {report_filename}')
        
        # Load assumptions.py
        assumptions = load_assumptions()
        print(f'✓ Successfully loaded assumptions\n')
        
        # Create report_{timestamp}.ipynb
        report.initialize(assumptions)
        report.create(report_filename)
        
        for calib in calib_scheme:
            if 'substitutions' in calib:
                for subs in calib['substitutions']:
                    sub_name = subs['name']
                    sub_repl = subs['repl']
                    calib_id += 1
                    # Run current calibration and update assumptions dict
                    self.run(calib_id, calib['name'], sub_name, sub_repl, report_filename, timestamp, assumptions)
                    print('\n')
            else:
                calib_id += 1
                # Run current calibration and update assumptions dict
                self.run(calib_id, calib['name'], None, {}, report_filename, timestamp, assumptions)
                print('\n')
                
        report.finish(report_filename, assumptions)
        return
    
def load_calibration_scheme(path):
    """
    Load a sequence of calibrations (a list of calibration names in a .txt file)
    """
    with open(path) as f:
        return eval(f.read()) # calibration_scheme.py should be a Python dict
    
def load_exopy_template(calib):
    """
    Load an Exopy template defining a specific calibration
    """
    with open(f'calibrations/{calib}/{calib}_template.meas.ini') as f:
        return f.read()
    
def load_assumptions():
    """
    Parse a dict of assumptions
    """
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