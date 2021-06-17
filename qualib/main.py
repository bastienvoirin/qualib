import os
import sys
import json
import traceback
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
        Runs a single calibration with given assumptions and Exopy template
        """
        global log

        full = f'{calib_name}_{sub_name}' if sub_name else calib_name
        prefix = full+':'

        log.info(prefix, f'Starting calibration with {len(sub_repl)} substitution{"s" if len(sub_repl) > 1 else ""}')
        log.info(prefix, log.json(sub_repl))
        
        try:
            Calibration = load_utils(log, calib_name, sub_name)
            exopy_templ = load_exopy_template(log, calib_name, sub_name)
            
            log.info(prefix, f'Generating "qualib/calibrations/{calib_name}/{calib_name}.meas.ini"')
            calibration = Calibration(log, exopy_templ, assumptions, calib_id, calib_name, sub_name, sub_repl, timestamp)
            
            log.info(prefix, 'Pre-processing')
            calibration.pre_process(calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions)

            log.info(prefix, 'Calling Exopy')
            ini_path = str(Path(os.path.realpath(__file__)).parent / f'calibrations/{calib_name}/{calib_name}.meas.ini')
            subprocess.run(['python', '-m', 'exopy', '-s', '-x', ini_path], capture_output=True, shell=True)

            log.info(prefix, 'Processing')
            calibration.process(calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions)
            log.info(prefix, 'Post-processing')
            calibration.post_process(calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions)

        except:
            log.error(prefix, f'{sys.exc_info()[1]}')
            [log.error('', line) for line in traceback.format_exc().splitlines()]
            print(f'{"="*70}\n\nAn error occurred while processing "{calib_name}" calibration: ', end='')
            print(f'{sys.exc_info()[1]}\nSee traceback below.\n\n{"#"*70}\n')
            raise # Propagate the exception to show the stack trace and prevent the next calibration

        return
    
    def run_all(self, pkg_calib_scheme):
        """
        Runs a calibration scheme with given Exopy templates, assumptions and utils
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
        
        assumptions = load_assumptions(log)
        
        log.info('', f'Initializing "reports/report_{timestamp}.ipynb"')
        report.initialize(assumptions, calib_scheme_str)

        log.info('', f'Creating "reports/report_{timestamp}.ipynb"')
        report.create(report_filename)
        
        print()
        for calib in calib_scheme:
            if 'substitutions' in calib:
                for subs in calib['substitutions']:
                    sub_name = subs['name']
                    sub_repl = subs['repl']
                    calib_id += 1
                    self.run(calib_id, calib['name'], sub_name, sub_repl, report_filename, timestamp, assumptions)
                    report.finish(report_filename, assumptions)
                    print()
            else:
                calib_id += 1
                self.run(calib_id, calib['name'], None, {}, report_filename, timestamp, assumptions)
                report.finish(report_filename, assumptions)
                print()
                
        log.info('', 'Done')
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
