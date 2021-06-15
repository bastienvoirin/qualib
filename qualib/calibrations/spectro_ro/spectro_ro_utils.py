from ..default import DefaultCalibration, DefaultJupyterReport
import json

class Calibration(DefaultCalibration): 
    def process(self, calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions):
        """
        Analyze and report the current calibration
        """
        repl = {'§TYPE§': sub_repl['TYPE']}
        cells = self.pre_process(calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions, repl)
        
        assumptions['readout']['freq'] = self.results['freq']
        
        repl = {'§FREQ§': f'{self.results["freq"]:.3f}'}
        self.post_process(calib_name, report_filename, cells, repl)
