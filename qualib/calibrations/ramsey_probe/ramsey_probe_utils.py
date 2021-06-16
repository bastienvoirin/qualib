from ..default import DefaultCalibration, DefaultJupyterReport
import json

class Calibration(DefaultCalibration): 
    def process(self, calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions):
        """
        Analyze and report the current calibration
        """
        repl = {'§FREQ§': str(assumptions['ramsey']['freq'])}
        cells = self.pre_process(calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions, repl)
        
        repl = {'§DELTA_F§': f'{self.results["delta_fr"]:.6f}'}
        self.post_process(calib_name, report_filename, cells, repl)