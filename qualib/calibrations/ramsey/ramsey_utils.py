from ..default import DefaultCalibration, DefaultJupyterReport
import json

class Calibration(DefaultCalibration): 
    def process(self, calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions):
        """
        Analyze and report the current calibration
        """
        repl = {
            '§FREQ§': str(assumptions['ramsey']['freq'])
        }
        cells = self.pre_report(calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions, repl)
        
        assumptions['qubit']['freq'] = self.result['f_LO']
        assumptions['ramsey']['freq'] = self.result['f_LO'] - assumptions['ramsey']['delta_freq']
        
        repl = {
            '§f_LO§': f'{self.result["f_LO"]:.6f}',
            '§T2§':   f'{abs(self.result["T2"])/1000:.3f}',
        }
        self.post_report(report_filename, cells, repl)