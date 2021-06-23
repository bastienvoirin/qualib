from ..default import DefaultCalibration

class Calibration(DefaultCalibration):
    def handle_substitutions(self) -> None:
        super().handle_substitutions()

    def pre_process(self) -> None:
        super().pre_process(mapping = {})

    def process(self) -> None:
        super().process()
        self.assumptions['rabi']['npoints'] = int(self.assumptions['rabi_probe']['npoints'] * 10 / self.results['samples_per_period'])
        #self.assumptions['rabi']['unconditional_pi2_pulse_linearity_amp_limit'] = self.results['linearity_amp_limit']
        #self.assumptions['rabi']['unconditional_pi_pulse_linearity_amp_limit']  = self.results['linearity_amp_limit']
        #self.assumptions['rabi']['conditional_pi_pulse_linearity_amp_limit']    = self.results['linearity_amp_limit']

    def post_process(self) -> None:
        super().post_process(mapping = {
            'PULSE_LENGTH':        f'{self.assumptions["rabi_probe"]["pulse_length"]}',
            'LINEARITY_AMP_LIMIT': f'{self.results["linearity_amp_limit"]:f}'
        })