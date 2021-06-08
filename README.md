Qualib provides automatic calibrations for experiments of superconducting quantum circuits, based on [Exopy](https://github.com/Exopy/exopy).

# Usage

```bash
python qualib.py calibration_scheme.py
```

Where `calibration_scheme.py` defines the calibration sequence file to run (see below).

# Structure

```text
├─ README.md
├─ exopy
│  └─
├─ exopy_env
│  └─
├─ measurements
│  └─
└─ qualib
   ├─ qualib.py
   ├─ assumptions.py
   ├─ calibration_scheme.py
   └─ calibrations
      ├─ default.py
      ├─ rabi_probe
      │  ├─ rabi_probe_utils.py
      │  ├─ rabi_probe_template.meas.ini
      │  └─ template_rabi_probe.ipynb
      ├─ rabi
      │  ├─ rabi_utils.py
      │  ├─ rabi_template.meas.ini
      │  ├─ template_rabi.ipynb
      │  └─ examples
      │     ├─ assumptions.py
      │     └─ calibration_scheme.py
      ├─ t1_qubit
      │  ├─ t1_qubit_utils.py
      │  └─ template_t1_qubit.ipynb
      └─ ramsey
         └─ ramsey_utils.py
```

# Calibration sequence

## `calibration_scheme.py`

- Format: Python list of calibration dictionaries with `<str>name` and `<list>substitutions`; each substitution is a dictionary with `<str>name` and `<dict>repl` dict of `"PLACEHOLDER": "replacement"` pairs
- Example: Rabi unconditional pi/2 pulse, unconditional pi pulse and conditional pi pulse

```python
[
    {"name": "rabi", "substitutions": [{"name": "uncond_pi2",
                                        "repl": {"PULSE_LENGTH": "unconditional_pi2_pulse_length",
                                                 "PULSE_AMP":    "unconditional_pi2_pulse_amp"}},
                                       {"name": "uncond_pi",
                                        "repl": {"PULSE_LENGTH": "unconditional_pi_pulse_length",
                                                 "PULSE_AMP":    "unconditional_pi_pulse_amp"}},
                                       {"name": "cond_pi",
                                        "repl": {"PULSE_LENGTH": "conditional_pi_pulse_length",
                                                 "PULSE_AMP":    "conditional_pi_pulse_amp"}}]}
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
