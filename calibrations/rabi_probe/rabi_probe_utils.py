from ..default import DefaultCalibration, DefaultJupyterReport
import json

class Calibration(DefaultCalibration):
    """
    meas.ini file generator from Exopy template and assumptions file
    Calibration-specific report generator
    """     
    def process(self, calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions):
        """
        Analyze and report the current calibration
        """
        repl = {}
        cells = self.pre_report(calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions, repl)
        assumptions['rabi']['npoints'] = int(assumptions['rabi_probe']['npoints'] * 10 / self.result['samples_per_period'])
        assumptions['rabi']['unconditional_pi2_pulse_linearity_amp_limit'] = self.result['linearity_amp_limit']
        assumptions['rabi']['unconditional_pi_pulse_linearity_amp_limit']  = self.result['linearity_amp_limit']
        assumptions['rabi']['conditional_pi_pulse_linearity_amp_limit']    = self.result['linearity_amp_limit']
        repl = {
            '§PULSE_LENGTH§':        f'{assumptions["rabi_probe"]["pulse_length"]}',
            '§LINEARITY_AMP_LIMIT§': f'{self.result["linearity_amp_limit"]:f}'
        }
        for key, val in repl.items():
            cells = cells.replace(key, val)
        cells_json = json.loads(cells)['cells']
        self.post_report(report_filename, cells_json)
        return
    
class JupyterReport(DefaultJupyterReport):
    pass
