from ..default import DefaultCalibration

class Calibration(DefaultCalibration):
    def handle_substitutions(self) -> None:
        super().handle_substitutions()

    def pre_process(self) -> None:
        super().pre_process(mapping = {
            'FREQ': str(self.assumptions['qubit']['freq']),
            'T2':   str(self.assumptions['qubit']['T2'])
        })

    def process(self) -> None:
        super().process()
        self.assumptions['qubit']['freq'] = self.results['f_LO']
        self.assumptions['qubit']['T2']   = self.results['T2_qubit']

    def post_process(self) -> None:
        super().post_process(mapping = {
            'f_LO': f'{self.results["f_LO"]:.6f}',
            'qubit_T2':   f'{abs(self.results["T2_qubit"])/1000:.3f}',
        })