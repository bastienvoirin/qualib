from ..default import DefaultCalibration, DefaultJupyterReport
import json

class Calibration(DefaultCalibration): 
    def process(self, calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions):
        """
        Analyze and report the current calibration
        """
        repl = {
            '§TYPE§': sub_repl['TYPE']
        }
        cells = self.pre_report(calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions, repl)
        if sub_name == 'circle_fit':
            assert self.results['fr_err'] < self.results['delta_fr'], 'Circle fit failed (too large fr_err)'
        assumptions['readout']['freq'] = self.results['freq']
        repl = {
            '§FREQ§': f'{self.results["freq"]:.3f}'
        }
        self.post_report(report_filename, cells, repl)
