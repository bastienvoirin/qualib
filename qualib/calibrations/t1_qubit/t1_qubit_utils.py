from ..default import DefaultCalibration

class Calibration(DefaultCalibration):
    def handle_substitutions(self) -> None:
        super().handle_substitutions()

    def pre_process(self) -> None:
        super().pre_process({
            'T1': str(self.assumptions['qubit']['T1'])
        })

    def process(self) -> None:
        super().process()
        wait_max_limit = int(self.assumptions['t1_qubit']['num_t1'] * self.results['T1_qubit'])
        self.assumptions['t1_qubit']['wait_max'] = max(self.assumptions['t1_qubit']['wait_max'], wait_max_limit)
        self.assumptions['ramsey']['wait_max']   = max(self.assumptions['ramsey']['wait_max'],   wait_max_limit)
        self.assumptions['qubit']['T1']          = self.results['T1_qubit']

    def post_process(self) -> None:
        super().post_process(mapping = {
            'T1_QUBIT': f'{self.results["T1_qubit"]/1000:.3f}'
        })