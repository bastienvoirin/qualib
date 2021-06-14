from ..default import DefaultCalibration, DefaultJupyterReport
import json

class Calibration(DefaultCalibration): 
    def process(self, calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions):
        """
        Analyze and report the current calibration
        """
        repl = {}
        cells = self.pre_report(calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions, repl)
        
        assumptions['readout']['freq'] = self.result['freq']
        
        repl = {
            '§FREQ§': f'{self.result["freq"]:.3f}'
        }
        self.post_report(report_filename, cells, repl)
