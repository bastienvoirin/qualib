from ..default import DefaultCalibration, DefaultJupyterReport
import json

class Calibration(DefaultCalibration): 
    def pre_process(self, calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions):
        repl = {'§TYPE§': sub_repl['TYPE']}
        self.cells = super().pre_process(calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions, repl)

    def process(self, calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions):
        assumptions['readout']['freq'] = self.results['freq']
        return calib_name, report_filename

    def post_process(calib_name, report_filename, cells):
        repl = {'§FREQ§': f'{self.results["freq"]:.3f}'}
        super().post_process(calib_name, report_filename, cells, repl)
