from ..default import DefaultCalibration, Report
import json

class Calibration(DefaultCalibration): 
    def process(self, calib_name, calib_id, subs_name, subs_misc, report_filename, timestamp, assumptions):
        """
        Analyze and report the current calibration
        """
        repl = {}
        cells = self.pre_process(calib_name, calib_id, subs_name, subs_misc, timestamp, assumptions, repl)
        
        wait_max_limit = int(assumptions['t1_qubit']['num_t1'] * self.results['t1_qubit'])
        assumptions['t1_qubit']['wait_max'] = max(assumptions['t1_qubit']['wait_max'], wait_max_limit)
        assumptions['ramsey']['wait_max'] = max(assumptions['ramsey']['wait_max'], wait_max_limit)
        
        repl = {'§T1_QUBIT§': f'{self.results["t1_qubit"]/1000:.3f}'}
        self.post_process(calib_name, report_filename, cells, repl)
