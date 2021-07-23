import numpy as np
import time
import datetime
from copy import deepcopy
from qualib.load import load_assumptions
from qualib.main import Qualib
from qualib.log import Log

qualib = Qualib()
log = Log()

def flux_sweep(calibration_scheme: list = [], min_flux: float = -0.5, max_flux: float = 0.5,
               curr_flux: float = 0.0, flux_step:float = 0.1, npoints: int = -1):
    """Scan a flux range and execute a given calibration sequence.

    """
    neg = np.arange(curr_flux, min_flux-flux_step, -flux_step)
    pos = np.arange(curr_flux, max_flux, flux_step)+flux_step

    results_filename = "flux_sweep_results" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    f = open(results_filename, 'w')
    f.close()

    all_calibs = []
    pt = 0
    for flux in [*neg, *pos]:
        for i in range(len(calibration_scheme)):
            calibration_scheme[i]["substitutions"] = calibration_scheme[i].get("substitutions") or {}
            calibration_scheme[i]["substitutions"]["$flux"] = str(flux)
        [all_calibs.append(deepcopy(calib)) for calib in calibration_scheme]
        pt += 1
        if pt == npoints:
            break

    print([calibration["substitutions"]['$flux'] for calibration in all_calibs])
    assumptions = load_assumptions(log, 'flux_sweep_assumptions.py')

    start_time = time.perf_counter()
    qualib.run_all(all_calibs, assumptions)
    stop_time = time.perf_counter()

    print(f'{(stop_time-start_time)/60:.2f} min (total)')
    print(f'{(stop_time-start_time)/60/pt:.2f} min/pt')