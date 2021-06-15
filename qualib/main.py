import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, time
from .load import load_calibration_scheme, load_assumptions, load_exopy_template, load_utils
from .log import Log
from .calibrations.default import DefaultJupyterReport

class Qualib:
    """
    Wrapper supclass
    """
    def run(self, calib_id, calib_name, sub_name, sub_repl, report_filename, timestamp, assumptions):
        """
        Run a single calibration with given assumptions and Exopy template
        """
        global log
        p1 = "_"+sub_name if sub_name else ""
        p2 = len(sub_repl)
        p3 = " s"[len(sub_repl)>1]
        print(f'Starting a "{calib_name}{p1}" calibration with {p2} substitution{p3}', end='')
        if sub_repl:
            print(':\n    '+'\n    '.join(map(lambda pair: f'{pair[0]} => {pair[1]}', sub_repl.items())))
        else:
            print()
        
        try:
            # Dynamically import Calibration from calibrations/{name}/{name}_utils.py
            Calibration = load_utils(log, calib_name)
            print(f'✓ Successfully loaded {calib_name}_utils.py')
            
            # Load calibrations/{name}/{name}_template.meas.ini
            exopy_templ = load_exopy_template(log, calib_name)
            print(f'✓ Successfully loaded Exopy template for "{calib_name}"\n  Generating {calib_name}.meas.ini file...')
            
            # Generate and save calibrations/{name}/{name}.meas.ini
            calibration = Calibration(log, exopy_templ, assumptions, calib_id, calib_name, sub_name, sub_repl, timestamp)
            keys = calibration.keys
            print(f'✓ Successfully saved {calib_name}.meas.ini in calibrations/{calib_name}')
            
            # Run 'python -m exopy -s -x ./calibrations/{name}/{name}.meas.ini' and capture output
            print(f'  Calling Exopy to run a "{calib_name}{f"_{sub_name}" if sub_name else ""}" calibration...\n')
            ini_path = str(Path(os.path.realpath(__file__)).parent / f'calibrations/{calib_name}/{calib_name}.meas.ini')
            subprocess.run(['python', '-m', 'exopy', '-s', '-x', ini_path], shell=True)
            #process = subprocess.run(['python', '-m', 'exopy', '-s', '-x', ini_path], capture_output=True)#, shell=True)
            #print(process.stdout.decode('utf-8').replace('\\n', '\n').replace('\\\'', '\''))
            
            # Process the hdf5 output file and report the result(s)
            calibration.process(calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions)
        except:
            print(f'{"="*70}\n\nAn error occurred while processing "{calib_name}" calibration: ', end='')
            print(f'{sys.exc_info()[1]}\nSee traceback below.\n\n{"#"*70}\n')
            raise # Propagate the exception to show the stack trace and prevent the next calibration
        return
    
    def run_all(self, pkg_calib_scheme):
        """
        Run a calibration scheme with given Exopy templates, assumptions and utils
        """
        global missing_calib_scheme
        assert len(sys.argv) > 1 or pkg_calib_scheme, missing_calib_scheme
        calib_scheme_path = ''
        if len(sys.argv) > 1:
            calib_scheme_path = sys.argv[1]
        else:
            calib_scheme_path = pkg_calib_scheme
            
        global log
        now = datetime.now()
        timestamp = now.strftime('%y_%m_%d_%H%M%S')
        report_filename = f'reports/report_{timestamp}.ipynb'
        report = DefaultJupyterReport()
        log.initialize(timestamp)
        calib_id = 0
        calib_scheme, calib_scheme_str = load_calibration_scheme(log, calib_scheme_path)
        print(f'\n\nStarting calibration sequence => {report_filename}')
        
        # Load assumptions.py
        assumptions = load_assumptions(log)
        print(f'✓ Successfully loaded assumptions\n')
        
        # Create report_{timestamp}.ipynb
        report.initialize(assumptions, calib_scheme_str)
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
        # [NbConvertApp] WARNING | No handler found for comm target 'matplotlib'
        #subprocess.run(['jupyter', 'nbconvert', '--execute', report_filename, '--to', 'notebook', '--inplace'])
        return
    
missing_calib_scheme = '''Missing calibration scheme

CLI usage:
    python -m qualib.main calibration_scheme.py

Package usage:
    pip install qualib
  then
    from qualib.main import Qualib
    qualib = Qualib()
    qualib.run_all('calibration_scheme.py')'''

log = Log()
if __name__ == '__main__':
    qualib = Qualib()
    qualib.run_all('')
