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
        ##############################################################

    def post_process(self):
        ##############################################################
        mapping = {}
        ##############################################################
        super().post_process(mapping)