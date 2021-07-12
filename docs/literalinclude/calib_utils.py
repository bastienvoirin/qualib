from .default import DefaultCalibration

class Calibration(DefaultCalibration):
    def handle_substitutions(self) -> None:
        # Define substitutions here
        super().handle_substitutions()

    def pre_process(self) -> None:
        super().pre_process(mapping = {})

    def process(self) -> None:
        super().process()
        # Update assumptions here

    def post_process(self) -> None:
        super().post_process(mapping = {})
