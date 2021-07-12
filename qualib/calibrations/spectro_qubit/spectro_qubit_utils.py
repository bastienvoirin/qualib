from ..default import DefaultCalibration
import re

class Calibration(DefaultCalibration):
    def handle_substitutions(self) -> None:
        sweep_width   = self.assumptions['spectro_qubit'][f'{self.substitutions["TYPE"]}_sweep_width']
        sweep_npoints = self.assumptions['spectro_qubit'][f'{self.substitutions["TYPE"]}_npoints']
        super().handle_substitutions({
            '$spectro_qubit/SWEEP_STEP':       f'{sweep_width/(sweep_npoints-1):.4f}',
            '$spectro_qubit/SWEEP_HALF_WIDTH': str(sweep_width/2)
        })

    def pre_process(self) -> None:
        super().pre_process(mapping = {
            'PULSE_LENGTH': str(self.assumptions['spectro_qubit'][f'{self.substitutions["NAME"]}_pulse_length']),
            'PULSE_AMP':    str(self.assumptions['spectro_qubit'][f'{self.substitutions["NAME"]}_pulse_amp'])
        })

    def process(self) -> None:
        super().process()
        self.assumptions['qubit']['freq'] = self.results['freq']

    def post_process(self) -> None:
        super().post_process(mapping = {
            'TYPE': self.substitutions['TYPE'],
            'FREQ': f'{self.results["freq"]:f}',
        })