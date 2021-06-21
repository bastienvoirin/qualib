from ..default import DefaultCalibration, Report
import json

class Calibration(DefaultCalibration):  
    def process(self, calib_name, calib_id, subs_name, subs_misc, report_filename, timestamp, assumptions):
        """
        Analyze and report the current calibration
        """
        repl = {}
        cells = self.pre_process(calib_name, calib_id, subs_name, subs_misc, timestamp, assumptions, repl)
        
        assumptions['rabi']['npoints'] = int(assumptions['rabi_probe']['npoints'] * 10 / self.results['samples_per_period'])
        assumptions['rabi']['unconditional_pi2_pulse_linearity_amp_limit'] = self.results['linearity_amp_limit']
        assumptions['rabi']['unconditional_pi_pulse_linearity_amp_limit']  = self.results['linearity_amp_limit']
        assumptions['rabi']['conditional_pi_pulse_linearity_amp_limit']    = self.results['linearity_amp_limit']
        
        repl = {
            '§PULSE_LENGTH§':        f'{assumptions["rabi_probe"]["pulse_length"]}',
            '§LINEARITY_AMP_LIMIT§': f'{self.results["linearity_amp_limit"]:f}'
        }
        self.post_process(calib_name, report_filename, cells, repl)
