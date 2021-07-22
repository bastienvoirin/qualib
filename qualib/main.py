import os
from re import sub
import sys
import json
import traceback
import subprocess
from copy import deepcopy

from pathlib import Path
from datetime import datetime, time
from typing import List, Dict, Union

from numpy.lib.function_base import place
from .load import load_calibration_scheme, load_assumptions
from .load import load_exopy_template, load_utils
from .log import Log
from .calibrations.default import Report

class Qualib:
    """Wrapper supclass.

    """

    retries = 0
    
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
        log_info(*log.json(substitutions))
        
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
            assumptions = deepcopy(calibration.assumptions)
            Qualib.retries = 0
            return deepcopy(assumptions)
        except KeyboardInterrupt:
            log.error(prefix, f'{sys.exc_info()[1]}')
            for line in traceback.format_exc().splitlines():
                log.error('', line)
            raise # Propagate the exception to show the stack
                  # trace and prevent the next calibration
        except:
            log.error(prefix, f'{sys.exc_info()[1]}')
            for line in traceback.format_exc().splitlines():
                log.error('', line)
            if Qualib.retries < (assumptions.get('retries') or 0):
                log_info('Retrying ')
                Qualib.retries += 1
                return self.run(log, report, assumptions, id,
                                name, substitutions, timestamp)
            Qualib.retries = 0
            raise # Propagate the exception to show the stack
                  # trace and prevent the next calibration
        
    
    def run_all(self, pkg_calib_scheme: Union[str, list] = '', assumptions: dict = {}) -> None:
        """Runs a calibration sequence whose path is either passed:
        
            * As ``pkg_calib_scheme`` --- package usage examples:
              ``Qualib().run_all('calibration_scheme.py', assumptions_dict)``, ``Qualib().run_all(calibration_scheme_list)``
            * Or in ``sys.argv`` --- CLI/module usage:
              ``python -m qualib.main calibration_scheme.py``.
        
        Args:
            pkg_calib_scheme: Path to the Python file defining
                              the calibration sequence to run (``str``)
                              or calibration sequence to run (``list``).
            assumptions: Optional. Custom assumptions ``dict``.
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
        log.show_debug_messages = True
        
        def log_info(*lines):
            log.info('', *lines) # Define global prefix here

        if type(pkg_calib_scheme) is list:
            seq_list, seq_str = pkg_calib_scheme, json.dumps(pkg_calib_scheme, indent=4)
        else:
            log_info(f'Reading and parsing "{calib_scheme_path}"')
            seq_list, seq_str = load_calibration_scheme(log, calib_scheme_path)

        if not assumptions:
            log_info('Reading and parsing "assumptions.py"')
            assumptions = load_assumptions(log)

        report_path = f'reports/report_{timestamp}.ipynb'
        log_info(f'Initializing "{report_path}"')
        report = Report(log, report_path, assumptions, seq_str)

        log_info('Starting calibration sequence')
        assumptions_ls = []
        for id, calibration in enumerate(seq_list, start=1):
            substitutions = calibration.get('substitutions') or {}
            if not substitutions.get('NAME'):
                substitutions = {'NAME': ''}
            assumptions_ls += [self.run(log, report, assumptions, id, calibration['name'],
                                       substitutions, timestamp)]
            with open(f"logs/{timestamp}.json", "w") as f:
                f.write(json.dumps(assumptions_ls, indent=4))
            assumptions = {}
            assumptions = deepcopy(assumptions_ls[-1])
        log_info('Done')
        return assumptions_ls

if __name__ == '__main__':
    qualib = Qualib()
    qualib.run_all()