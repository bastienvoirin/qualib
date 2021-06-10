from ..default import DefaultCalibration, DefaultJupyterReport
import json

class Calibration(DefaultCalibration): 
    def process(self, calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions):
        """
        Analyze and report the current calibration
        """
        repl = {}
        cells = self.pre_report(calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions, repl)
        
        wait_max_limit = int(assumptions['t1_qubit']['num_t1'] * self.result['t1_qubit'])
        assumptions['t1_qubit']['wait_max'] = max(assumptions['t1_qubit']['wait_max'], wait_max_limit)
        assumptions['ramsey']['wait_max'] = max(assumptions['ramsey']['wait_max'], wait_max_limit)
        
        repl = {
            '§T1_QUBIT§': f'{self.result["t1_qubit"]/1000:.3f}'
        }
        self.post_report(report_filename, cells, repl)