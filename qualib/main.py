import os
import sys
import json
import traceback
import subprocess

from pathlib import Path
from datetime import datetime, time
from .load import load_calibration_scheme, load_assumptions, load_exopy_template, load_utils
from .log import Log
from .calibrations.default import Report

class Qualib:
    """Wrapper supclass

    """
    def run(self, log, report, assumptions, calib_id, calib_name, subs_name, subs_misc):
        """Runs a single calibration with given assumptions and Exopy template

        """
        full = f'{calib_name}_{subs_name}' if subs_name else calib_name
        prefix = full+':'

        log.info(prefix, f'Starting calibration with {len(subs_misc)} substitution{"s" if len(subs_misc) > 1 else ""}')
        log.info(prefix, log.json(subs_misc))
        
        try:
            Calibration = load_utils(log, calib_name, subs_name)
            exopy_templ = load_exopy_template(log, calib_name, subs_name)
            
            log.info(prefix, f'Generating "qualib/calibrations/{calib_name}/{calib_name}.meas.ini"')
            calibration = Calibration(log, exopy_templ, assumptions, calib_id, calib_name, subs_name, subs_misc)
            
            log.info(prefix, 'Pre-processing')
            calibration.pre_process(log, report, assumptions, calib_name, calib_id, subs_name, subs_misc)

            log.info(prefix, 'Calling Exopy')
            ini_path = str(Path(os.path.realpath(__file__)).parent / f'calibrations/{calib_name}/{calib_name}.meas.ini')
            subprocess.run(['python', '-m', 'exopy', '-s', '-x', ini_path], capture_output=True, shell=True)

            log.info(prefix, 'Processing')
            calibration.process(log, report, assumptions, calib_name, calib_id, subs_name, subs_misc)
            log.info(prefix, 'Post-processing')
            calibration.post_process(log, report, assumptions, calib_name, calib_id, subs_name, subs_misc)

        except:
            log.error(prefix, f'{sys.exc_info()[1]}')
            [log.error('', line) for line in traceback.format_exc().splitlines()]
            print(f'{"="*70}\n\nAn error occurred while processing "{calib_name}" calibration: ', end='')
            print(f'{sys.exc_info()[1]}\nSee traceback below.\n\n{"#"*70}\n')
            raise # Propagate the exception to show the stack trace and prevent the next calibration

        return
    
    def run_all(self, pkg_calib_scheme):
        """Runs a calibration scheme with given Exopy templates, assumptions and utils

        :param str pkg_calib_scheme: Path to the Python file defining the calibration sequence to run
        :type pkg_calib_scheme: str, optional
        """
        global missing_calib_scheme
        assert len(sys.argv) > 1 or pkg_calib_scheme, missing_calib_scheme
        calib_scheme_path = ''
        if len(sys.argv) > 1:
            calib_scheme_path = sys.argv[1]
        else:
            calib_scheme_path = pkg_calib_scheme
            
        timestamp = datetime.now().strftime('%y_%m_%d_%H%M%S')

        log = Log()
        log.initialize(timestamp)

        calib_scheme, calib_scheme_str = load_calibration_scheme(log, calib_scheme_path)
        assumptions = load_assumptions(log)

        log.info('', f'Initializing "reports/report_{timestamp}.ipynb"')
        report = Report(f'reports/report_{timestamp}.ipynb', assumptions, calib_scheme_str)

        log.info('', 'Starting calibration sequence')

        for calib_id, calib in enumerate(calib_scheme, start=1):
            self.run(log, report, assumptions, calib_id, calib['name'], calib.get('substitutions') or {})
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

if __name__ == '__main__':
    qualib = Qualib()
    qualib.run_all()
