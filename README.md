[![Documentation Status](https://readthedocs.org/projects/qualib/badge/?version=latest)](https://qualib.readthedocs.io/en/latest/?badge=latest)

Qualib provides automatic calibrations for experiments on superconducting quantum circuits, based on [Exopy](https://github.com/Exopy/exopy).

# Installation

1. `git clone https://github.com/bastienvoirin/qualib.git`
1. `pip install .` (or `pip install <path to local Qualib repository>`)

# Usage


`calibration_scheme.py` defines the calibration sequence file to run.

## CLI/module usage

```
python -m qualib.main calibration_scheme.py
```


## Package usage

```python
from qualib.main import Qualib

qualib = Qualib()
qualib.run_all('calibration_scheme.py')
```

# Calibration sequence

## `assumptions.py`

`assumptions.py` should be a Python dictionary of depth 1 or 2.

## `calibration_scheme.py`

`calibration_scheme.py` should be a Python list. Each element of this list specifies a calibration to run.

Format:

```python
[
    {"name": "a_calibration"},
    
    {"name": "another_calibration",
     "substitutions": {"NAME":                "variant_in_camel_case",
                       "A_SUBSTITUTION":      "a_value",
                       "ANOTHER_SUBTITUTION": "another_value"}}
]
```

* `name`: the calibration name
* `substitutions`: an optional dictionary of substitutions; if present, `NAME` must be defined.


# Defining a calibration in `qualib/calibrations/`

See [https://qualib.readthedocs.io/en/latest/user_guide.html](https://qualib.readthedocs.io/en/latest/user_guide.html) for further explanations.

## `{calib_name}_template.meas.ini`

- Placeholders format: `$parameter` or `$section/parameter`, where `section` and `parameter` are alphanumeric strings (regex: `[a-zA-Z0-9_]`) and support substitutions
- Examples: `$averaging`, `$twpa/freq`, `$qubit/PULSE_LENGTH`
- See `Calibration(DefaultCalibration).__init__` in `{calib_name}_utils.py`

## `{calib_name}_utils.py`

## `template_{calib_name}.ipynb`

Typical Jupyter Notebook template:

```python
# Calibration name ({SUBSTITUTION})
## Result: {POST_PLACEHOLDER} unit

# load experimental data
file = h5py.File('HDF5_PATH', 'r', swmr=True)
xdata = file['data']['x'][()]
ydata = file['data']['y'][()];

# fit experimental data
popt, pcov = opt.curve_fit(function, xdata, ydata, guesses=(0, 1, 2))
f'a, b, c = {popt}'

# plot experimental data and curve fit(s)
fig, ax = plt.subplots()
ax.plot(xdata, ydata, '.-', label='Data')
ax.plot(xdata, function(xdata, *popt), label=f'Fit: a = {popt[0]:f}')
ax.legend();

# optional interfaces: raise an exception when any(np.sqrt(np.diag(_cov)) >= 0.05*_opt)
# where np.sqrt(np.diag(_cov)) gives the standard deviation on the optimized parameters
_opt = popt
_cov = pcov

# optional interface: raises an exception when a specific condition is met
_err = {'Custom error', _opt[0] < 0}

# mandatory interface
_results = {'a': popt[0]}
_results
```

This Jupyter notebook should be saved as `calib_name_template.ipynb` under `qualib/calibrations/calib_name`.
