{
    'default_path': 'F:/data/Qnode Fock_stab 2/calibrations',
    'filename': 'FILENAME', # {calib_id}_{calib_name}.h5
    'qubit': {
        'freq':                     4.441065, # updated by [ramsey]
        'power':                          12,
        'conditional_pi_pulse_length':   700,
        'conditional_pi_pulse_amp':        0, # updated by [rabi]
        'unconditional_pi_pulse_length':  52,
        'unconditional_pi_pulse_amp':      0, # updated by [rabi]
        'unconditional_pi2_pulse_length': 32,
        'unconditional_pi2_pulse_amp':     0, # updated by [rabi]
    },
    'readout': {
        'freq':   6.342,
        'power':  18,
        'length': 1000,
        'amp':    0.04
    },
    'twpa': {
        'freq':  5.788, # updated by [twpa]
        'power': 6      # updated by [twpa]
    },
    'averaging': 1000,
    
    ######## calibration-specific parameters ########
    
    'rabi_probe': {
        'npoints':      101,
        'max_amp':      0.4,
        'pulse_length': 1000
    },
    'rabi': {
        'npoints':                                     101,  # updated by [rabi_probe]
        'max_amp':                                     0.4,
        'unconditional_pi2_pulse_linearity_amp_limit': 0.31, # updated by [rabi_probe]
        'unconditional_pi_pulse_linearity_amp_limit':  0.24, # updated by [rabi_probe]
        'conditional_pi_pulse_linearity_amp_limit':    0.21  # updated by [rabi_probe]
    },
    'ramsey': {
        'long_ro_length': 1000,  # see $readout/length?
        'long_ro_amp':    0.04,  # see $readout/amp?
        'wait_min':       20,
        'wait_max':       30000, # updated by [t1_qubit]: $ramsey/wait_max ← max($ramsey_wait_max, 5*T1)
        'npoints':        51,
        'averaging':      5000,
        'freq':           4.441, # base frequency, updated by [ramsey]
                                 # $ramsey/freq ← $qubit/freq - $ramsey/delta_freq
        'width':          1e-3,  # frequencies ← (freq-width/2, freq, freq+width/2)
        'delta_freq':     5e-5   # defines $qubit/freq - $ramsey/freq
    },
    't1_qubit': {
        'num_t1':         8,     # wait_max will be adjusted to be greater or equal to §t1_qubit/num_t1 * T1
        'long_ro_length': 1000,  # see $readout/length?
        'long_ro_amp':    0.04,  # see $readout/amp?
        'wait_min':       20,
        'wait_max':       30000, # updated by [t1_qubit]
        'npoints':        51,
        'averaging':      5000
    },
    'spectro_ro': {
        'averaging': 10000
    }
}
