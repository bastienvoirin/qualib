[![Documentation Status](https://readthedocs.org/projects/qualib/badge/?version=latest)](https://qualib.readthedocs.io/en/latest/?badge=latest)

Qualib provides automatic calibrations for experiments on superconducting quantum circuits, based on [Exopy](https://github.com/Exopy/exopy).

# Usage

`calibration_scheme.py` defines the calibration sequence file to run (see below).

## As a module

```shell
python -m qualib.main calibration_scheme.py
```

## As a package

```shell
pip install qualib
```

```python
from qualib.main import Qualib

qualib = Qualib()
qualib.run_all('calibration_scheme.py')
```

# Structure

```text
├── assumptions.py
├── calibration_scheme.py
├── README.md
├── logs
│   └── README.md
├── reports
│   └── README.md
├── setup.py
└── qualib
    ├── __init__.py
    ├── qualib.py
    ├── load.py
    ├── log.py
    └── calibrations
        ├── __init__.py
        ├── default_header.ipynb
        ├── default.py
        ├── template_CALIBRATION_NAME.ipynb
        ├── rabi
        │   ├── rabi_template.meas.ini
        │   ├── rabi_utils.py
        │   └── template_rabi.ipynb
        ├── rabi_probe
        │   ├── rabi_probe_template.meas.ini
        │   ├── rabi_probe_utils.py
        │   └── template_rabi_probe.ipynb
        ├── ramsey
        │   ├── ramsey_template.meas.ini
        │   ├── ramsey_utils.py
        │   └── template_ramsey.ipynb
        ├── spectro_ro
        │   ├── spectro_ro_template.meas.ini
        │   ├── spectro_ro_utils.py
        │   └── template_spectro_ro.ipynb
        └── t1_qubit
            ├── t1_qubit_template.meas.ini
            ├── t1_qubit_utils.py
            └── template_t1_qubit.ipynb
```

# Calibration sequence

## `calibration_scheme.py`

- Format: Python list of calibration dictionaries with `<str>name` and `<list>substitutions`; each substitution is a dictionary with `<str>name` and `<dict>repl` dict of `"PLACEHOLDER": "replacement"` pairs
- Example:

```python
[
    {"name": "rabi_probe"},
    {"name": "rabi", "substitutions": [{"name": "uncond_pi2",
                                        "repl": {"PULSE": "unconditional_pi2_pulse",
                                                 "TYPE":  "unconditional pi/2 pulse"}},
                                       {"name": "uncond_pi",
                                        "repl": {"PULSE": "unconditional_pi_pulse",
                                                 "TYPE":  "unconditional pi pulse"}},
                                       {"name": "cond_pi",
                                        "repl": {"PULSE": "conditional_pi_pulse",
                                                 "TYPE":  "conditional pi pulse"}}]},
    {"name": "t1_qubit"},
    {"name": "ramsey"},
    {"name": "spectro_ro"}
]
```

## `assumptions.py`

# Defining a calibration in qualib/calibrations/

## `{calib_name}_template.meas.ini`

- Placeholders format: `$parameter` or `$section/parameter`, where `section` and `parameter` are alphanumeric strings (regex: `[a-zA-Z0-9_]`) and support substitutions
- Examples: `$averaging`, `$twpa/freq`, `$qubit/PULSE_LENGTH`
- See `Calibration(DefaultCalibration).__init__` in `{calib_name}_utils.py`

## `{calib_name}_utils.py`

## `template_{calib_name}.ipynb`

# Calibrations

## rabi_probe

A "Rabi probe" calibration consists in:

- A long pulse (> 750ns) with many points (100 to 1000)
- A running FFT
- A detection algorithm returning a linearity limit

## rabi

A "Rabi" calibration consists in:

- Conditional (long) or unconditional (short) pulses
- A cosine curve fit

## t1_qubit

A "T1 of qubit" calibration consists in:

- An exponential curve fit

## ramsey

## spectro_ro
