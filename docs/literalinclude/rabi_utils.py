from ..default import DefaultCalibration

class Calibration(DefaultCalibration):
    def handle_substitutions(self) -> None:
        super().handle_substitutions()

    def pre_process(self) -> None:
        super().pre_process({
            'LINEARITY_AMP_LIMIT': str(self.assumptions['rabi'][f'{self.substitutions["PULSE"]}_linearity_amp_limit'])
        })

    def process(self) -> None:
        super().process()
        self.assumptions['qubit'][f'{self.substitutions["PULSE"]}_amp'] = self.results['a_rabi']

    def post_process(self) -> None:
        factor = 1
        if '_pi_'  in self.substitutions['PULSE']: factor = 2
        if '_pi2_' in self.substitutions['PULSE']: factor = 4
        
        super().post_process({
            'TYPE':         self.assumptions['TYPE'],
            'PULSE_AMP':    f'{self.results["a_rabi"]/factor:f}',
            'PULSE_LENGTH': str(self.assumptions['qubit'][f'{self.substitutions["PULSE"]}_length'])
        })
