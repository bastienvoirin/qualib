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
        repl = {
            '§LINEARITY_AMP_LIMIT§': str(assumptions['rabi'][f'{sub_repl["PULSE"]}_linearity_amp_limit'])
        }
        cells = self.pre_report(calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions, repl)
        assumptions['qubit'][f'{sub_repl["PULSE"]}_amp'] = self.result['a_rabi']
        factor = 1
        if '_pi_'  in sub_repl['PULSE']: factor = 2
        if '_pi2_' in sub_repl['PULSE']: factor = 4
        repl = {
            '§TYPE§':         sub_repl['TYPE'],
            '§PULSE§':        f'\'{sub_repl["PULSE"]}\'',
            '§PULSE_AMP§':    f'{self.result["a_rabi"]/factor:f}',
            '§PULSE_LENGTH§': str(assumptions['qubit'][f'{sub_repl["PULSE"]}_length'])
        }
        for key, val in repl.items():
            cells = cells.replace(key, val)
        cells_json = json.loads(cells)['cells']
        self.post_report(report_filename, cells_json)
        return
    
class JupyterReport(DefaultJupyterReport):
    pass