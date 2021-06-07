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
      ├─ rabi
      │  ├─ rabi_utils.py
      │  ├─ rabi_template.meas.ini
      │  └─ template_rabi.ipynb
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

# Calibrations (`qualib/calibrations/{calib_name}/`)

## `{calib_name}_template.meas.ini`

- Placeholders format: `$parameter` or `$section/parameter`, where `section` and `parameter` are alphanumeric strings (regex: `[a-zA-Z0-9_]`) and support substitutions
- Examples: `$averaging`, `$twpa/freq`, `$qubit/PULSE_LENGTH`
- See `Calibration(DefaultCalibration).__init__` in `{calib_name}_utils.py`

## `{calib_name}_utils.py`

## `template_{calib_name}.ipynb`
