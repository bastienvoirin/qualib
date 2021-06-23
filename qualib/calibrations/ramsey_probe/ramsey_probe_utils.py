from ..default import DefaultCalibration

class Calibration(DefaultCalibration):
    def handle_substitutions(self) -> None:
        super().handle_substitutions()

    def pre_process(self) -> None:
        super().pre_process(mapping = {
            'FREQ': str(self.assumptions['ramsey']['freq'])
        })

    def process(self) -> None:
        super().process()

    def post_process(self) -> None:
        super().post_process(mapping = {
            'DELTA_F': f'{self.results["delta_fr"]:.6f}'
        })
        