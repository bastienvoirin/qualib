from ..default import DefaultCalibration, Report
import json

class Calibration(DefaultCalibration):  
    def process(self, calib_name, calib_id, subs_name, subs_misc, report_filename, timestamp, assumptions):
        """
        Analyze and report the current calibration
        """
        repl = {'LINEARITY_AMP_LIMIT': str(assumptions['rabi'][f'{subs_misc["PULSE"]}_linearity_amp_limit'])}
        cells = self.pre_process(calib_name, calib_id, subs_name, subs_misc, timestamp, assumptions, repl)
        
        assumptions['qubit'][f'{subs_misc["PULSE"]}_amp'] = self.results['a_rabi']
        factor = 1
        if '_pi_'  in subs_misc['PULSE']: factor = 2
        if '_pi2_' in subs_misc['PULSE']: factor = 4
        
        repl = {
            '§TYPE§':         subs_misc['TYPE'],
            '§PULSE_AMP§':    f'{self.results["a_rabi"]/factor:f}',
            '§PULSE_LENGTH§': str(assumptions['qubit'][f'{subs_misc["PULSE"]}_length'])
        }
        self.post_process(calib_name, report_filename, cells, repl)