from ..default import DefaultCalibration

class Calibration(DefaultCalibration):
    def handle_substitutions(self) -> None:
        super().handle_substitutions()

    def pre_process(self) -> None:
        super().pre_process(mapping = {
            'DELTA': str(self.assumptions['ramsey_t2']['delta']),
            'T2':    str(self.assumptions['qubit']['T2'])
        })

    def process(self) -> None:
        super().process()
        self.assumptions['qubit']['T2'] = self.results['T2_qubit']

    def post_process(self) -> None:
        super().post_process(mapping = {
            'qubit_T2': f'{self.results["T2_qubit"]:.3f}',
        })