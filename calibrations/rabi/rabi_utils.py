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
        cells = self.pre_report(calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions)
        cells = cells.replace('§TYPE§', sub_name)
        cells = cells.replace('§PULSE_LENGTH§', str(assumptions['qubit'][sub_repl['PULSE_LENGTH']]))
        cells = cells.replace('§PULSE_AMP§', f'{self.result["a_rabi"]:f}')
        cells_json = json.loads(cells)['cells']
        self.post_report(report_filename, cells_json)
        return
    
class JupyterReport(DefaultJupyterReport):
    pass