from ..default import DefaultCalibration

class Calibration(DefaultCalibration):
    def handle_substitutions(self):
        super().handle_substitutions()

    def pre_process(self):
        super().pre_process({'TYPE': self.substitutions.get('TYPE')})

    def process(self, assumptions):
        assumptions['readout']['freq'] = self.results.get('freq') or 0

    def post_process(self):
        super().post_process({'FREQ': f'{self.results.get("freq") or 0:.3f}'})