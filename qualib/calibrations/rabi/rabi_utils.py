from ..default import DefaultCalibration, DefaultJupyterReport
import json

class Calibration(DefaultCalibration):  
    def process(self, calib_name, calib_id, sub_name, sub_repl, report_filename, timestamp, assumptions):
        """
        Analyze and report the current calibration
        """
        repl = {'§LINEARITY_AMP_LIMIT§': str(assumptions['rabi'][f'{sub_repl["PULSE"]}_linearity_amp_limit'])}
        cells = self.pre_process(calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions, repl)
        
        assumptions['qubit'][f'{sub_repl["PULSE"]}_amp'] = self.results['a_rabi']
        factor = 1
        if '_pi_'  in sub_repl['PULSE']: factor = 2
        if '_pi2_' in sub_repl['PULSE']: factor = 4
        
        repl = {
            '§TYPE§':         sub_repl['TYPE'],
            '§PULSE_AMP§':    f'{self.results["a_rabi"]/factor:f}',
            '§PULSE_LENGTH§': str(assumptions['qubit'][f'{sub_repl["PULSE"]}_length'])
        }
        self.post_process(calib_name, report_filename, cells, repl)