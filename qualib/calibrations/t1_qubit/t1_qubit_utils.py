from ..default import DefaultCalibration

class Calibration(DefaultCalibration):
    def handle_substitutions(self) -> None:
        super().handle_substitutions()

    def pre_process(self) -> None:
        super().pre_process(mapping = {})

    def process(self, assumptions) -> None:
        super().process()
        wait_max_limit = int(assumptions['t1_qubit']['num_t1'] * self.results['t1_qubit'])
        assumptions['t1_qubit']['wait_max'] = max(assumptions['t1_qubit']['wait_max'], wait_max_limit)
        assumptions['ramsey']['wait_max']   = max(assumptions['ramsey']['wait_max'],   wait_max_limit)

    def post_process(self) -> None:
        super().post_process(mapping = {
            'T1_QUBIT': f'{self.results["t1_qubit"]/1000:.3f}'
        })