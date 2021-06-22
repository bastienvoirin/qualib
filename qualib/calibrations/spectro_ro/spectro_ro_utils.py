from ..default import DefaultCalibration

class Calibration(DefaultCalibration):
    def handle_substitutions(self):
        ##############################################################
        ##############################################################
        super().handle_substitutions()

    def pre_process(self):
        ##############################################################
        mapping = {}
        ##############################################################
        super().pre_process(mapping)

    def process(self, assumptions):
        super().process()
        ##############################################################
        assumptions['readout']['freq'] = self.results.get('freq') or 0
        ##############################################################

    def post_process(self):
        ##############################################################
        mapping = {'FREQ': f'{self.results.get("freq") or 0:.3f}'}
        ##############################################################
        super().post_process(mapping)