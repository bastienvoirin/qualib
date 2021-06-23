from ..default import DefaultCalibration

class Calibration(DefaultCalibration):
    def handle_substitutions(self) -> None:
        super().handle_substitutions()

    def pre_process(self) -> None:
        super().pre_process(mapping = {})

    def process(self) -> None:
        super().process()
        self.assumptions['readout']['freq'] = self.results.get('freq') or 0

    def post_process(self) -> None:
        super().post_process(mapping = {
            'FREQ': f'{self.results.get("freq") or 0:.3f}'
        })