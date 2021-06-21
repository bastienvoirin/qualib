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
    """Wrapper supclass.

    """
    def run(self, log, report, assumptions, id, name, substitutions):
        """Runs a single calibration with given assumptions and Exopy template.
        
        Args:
            log (Log):
            report (Report):
            assumptions (dict): The current state of the assumptions (updated after each calibration).
            id (int): A natural number giving the rank of the calibration to run.
            name (str): The name of the calibration to run.
            substitutions (dict): The dictionary of substitutions.
        
        Returns:
            `None`
        """
        full = f'{name}_{substitutions["name"]}' if substitutions['name'] else name
        prefix = full+':'

        log.info(prefix, f'Starting calibration with {len(substitutions)} substitution{"s" if len(substitutions) > 1 else ""}')
        log.info(prefix, log.json(substitutions))
        
        try:
            Calibration = load_utils(log, name, substitutions)
            exopy_templ = load_exopy_template(log, name, substitutions['name'])
            
            log.info(prefix, f'Generating "qualib/calibrations/{name}/{name}.meas.ini"')
            calibration = Calibration(log, report, assumptions, id, name, substitutions, exopy_templ, prefix)
            
            log.info(prefix, 'Handling substitutions')
            calibration.handle_substitutions()

            log.info(prefix, 'Pre-processing (handling pre-placeholders)')
            calibration.pre_process()

            log.info(prefix, 'Updating report')
            report.add_calibration(calibration)

            log.info(prefix, 'Calling Exopy')
            """
            ini_path = str(Path(os.path.realpath(__file__)).parent / f'calibrations/{name}/{name}.meas.ini')
            subprocess.run(['python', '-m', 'exopy', '-s', '-x', ini_path], capture_output=True, shell=True)
            """

            log.info(prefix, 'Processing (handling interfaces and updating assumptions)')
            calibration.process(assumptions)

            log.info(prefix, 'Post-processing')
            calibration.post_process()

            log.info(prefix, 'Reporting results')
            report.add_results(assumptions)

        except:
            log.error(prefix, f'{sys.exc_info()[1]}')
            [log.error('', line) for line in traceback.format_exc().splitlines()]
            print(f'{"="*70}\n\nAn error occurred while processing "{name}" calibration: ', end='')
            print(f'{sys.exc_info()[1]}\nSee traceback below.\n\n{"#"*70}\n')
            raise # Propagate the exception to show the stack trace and prevent the next calibration

        return
    
    def run_all(self, pkg_calib_scheme = ''):
        """Runs a calibration sequence whose path is either passed:
        
            * As ``pkg_calib_scheme`` --- package usage: ``Qualib().run_all('calibration_scheme.py')``
            * Or in ``sys.argv`` --- CLI/module usage: ``python qualib.main calibration_scheme.py``.
        
        Args:
            pkg_calib_scheme (`str`, optional): path to the Python file defining the calibration sequence to run.
        
        Returns:
            `None`
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

        log.info('', f'Reading and parsing "{calib_scheme_path}"')
        calib_scheme, calib_scheme_str = load_calibration_scheme(log, calib_scheme_path)

        log.info('', 'Reading and parsing "assumptions.py"')
        assumptions = load_assumptions(log)

        log.info('', f'Initializing "reports/report_{timestamp}.ipynb"')
        report = Report(f'reports/report_{timestamp}.ipynb', assumptions, calib_scheme_str)

        log.info('', 'Starting calibration sequence')

        for id, calibration in enumerate(calib_scheme, start=1):
            self.run(log, report, assumptions, id, calibration['name'], calibration.get('substitutions') or {'name': ''})
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
