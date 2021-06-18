from ..default import DefaultCalibration, DefaultJupyterReport
import json

class Calibration(DefaultCalibration): 
    def pre_process(self, calib_name, calib_id, subs_name, subs_misc, timestamp, assumptions):
        repl = {'§TYPE§': subs_misc['TYPE']}
        self.cells = super().pre_process(calib_name, calib_id, subs_name, subs_misc, timestamp, assumptions, repl)

    def process(self, calib_name, calib_id, subs_name, subs_misc, report_filename, timestamp, assumptions):
        assumptions['readout']['freq'] = self.results['freq']
        return calib_name, report_filename

    def post_process(calib_name, report_filename, cells):
        repl = {'§FREQ§': f'{self.results["freq"]:.3f}'}
        super().post_process(calib_name, report_filename, cells, repl)
