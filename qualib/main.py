import os
import sys
import json
import traceback
import subprocess

from pathlib import Path
from datetime import datetime, time
from typing import List, Dict
from .load import load_calibration_scheme, load_assumptions
from .load import load_exopy_template, load_utils
from .log import Log
from .calibrations.default import Report

class Qualib:
    """Wrapper supclass.

    """
    
    def run(self, log: Log, report: Report, assumptions: dict, id: int,
            name: str, substitutions: Dict[str, str], timestamp: str) -> None:
        """Runs a single calibration with given assumptions and Exopy template.
        
        Args:
            log: Logging object.
            report: Default report object.
            assumptions: Current state of the assumptions
                         (updated after each calibration).
            id: Natural number giving the rank of the calibration to run.
            name: Name of the calibration to run (in lowercase).
            substitutions: Dictionary of substitutions.
            timestamp: Timestamp used to create the log and report files.
        """
        subs_name = substitutions['NAME']
        full      = f'{name}_{subs_name}' if subs_name else name
        prefix    = full+':'
        
        def log_info(*lines):
            log.info(prefix, *lines) # Define calibration prefix here

        log_info(f'Starting calibration with {len(substitutions)} '
                 f'substitution{"s" if len(substitutions) > 1 else ""}')
        log_info(log.json(substitutions))
        
        try:
            Calibration = load_utils(log, name, prefix)
            exopy_templ = load_exopy_template(log, name, prefix)
            
            log_info('Initializing calibration')
            calibration = Calibration(log, report, assumptions, id, name,
                                      substitutions, exopy_templ, prefix,
                                      timestamp)
            
            log_info('Handling substitutions')
            calibration.handle_substitutions()

            log_info('Pre-processing (handling pre-placeholders)')
            calibration.pre_process()

            log_info('Updating report')
            report.add_calibration(calibration)

            log_info('Calling Exopy')
            part_one = Path(os.path.realpath(__file__)).parent
            part_two = f'calibrations/{name}/{name}.meas.ini'
            ini_path = str(part_one / part_two)
            subprocess.run(['python', '-m', 'exopy', '-s', '-x', ini_path],
                           capture_output=True, shell=True)
            
            log_info('Processing (fetching results and updating assumptions)')
            calibration.process()

            log_info('Post-processing')
            calibration.post_process()

            log_info('Reporting results')
            report.add_results(calibration)
            assumptions = dict(calibration.assumptions)

        except:
            log.error(prefix, f'{sys.exc_info()[1]}')
            for line in traceback.format_exc().splitlines():
                log.error('', line)
            raise # Propagate the exception to show the stack
                  # trace and prevent the next calibration
        return
    
    def run_all(self, pkg_calib_scheme: str = '') -> None:
        """Runs a calibration sequence whose path is either passed:
        
            * As ``pkg_calib_scheme`` --- package usage:
              ``Qualib().run_all('calibration_scheme.py')``
            * Or in ``sys.argv`` --- CLI/module usage:
              ``python -m qualib.main calibration_scheme.py``.
        
        Args:
            pkg_calib_scheme: path to the Python file defining
                              the calibration sequence to run.
        """
        assert len(sys.argv) > 1 or pkg_calib_scheme, '\n'.join([
            'Missing calibration scheme\n',
            '  CLI usage:',
            '    python -m qualib.main calibration_scheme.py\n',
            '  Package usage:',
            '      pip install qualib',
            '    then',
            '      from qualib.main import Qualib',
            '      qualib = Qualib()',
            '      qualib.run_all(\'calibration_scheme.py\')'
        ])

        calib_scheme_path = ''
        if len(sys.argv) > 1:
            calib_scheme_path = sys.argv[1]
        else:
            calib_scheme_path = pkg_calib_scheme
            
        timestamp = datetime.now().strftime('%y_%m_%d_%H%M%S')

        log = Log()
        log.initialize(timestamp)
        
        def log_info(*lines):
            log.info('', *lines) # Define global prefix here

        log_info(f'Reading and parsing "{calib_scheme_path}"')
        seq_list, seq_str = load_calibration_scheme(log, calib_scheme_path)

        log_info('Reading and parsing "assumptions.py"')
        assumptions = load_assumptions(log)

        report_path = f'reports/report_{timestamp}.ipynb'
        log_info(f'Initializing "{report_path}"')
        report = Report(log, report_path, assumptions, seq_str)

        log_info('Starting calibration sequence')
        for id, calibration in enumerate(seq_list, start=1):
            self.run(log, report, assumptions, id, calibration['name'],
                     calibration.get('substitutions') or {'NAME': ''}, timestamp)
        log_info('Done')
        return

if __name__ == '__main__':
    qualib = Qualib()
    qualib.run_all()