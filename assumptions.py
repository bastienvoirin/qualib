{
    'default_path': 'F:/data/Qnode Fock_stab 3/calibrations',
    'filename': 'FILENAME', # {calib_id}_{calib_name}.h5
    'retries': 3,
    'qubit': {
        'freq':                        4.440, # updated by [ramsey], [spectro_qubit]
        'power':                          12,
        'conditional_pi_pulse_length':   700,
        'conditional_pi_pulse_amp':        0, # updated by [rabi]
        'unconditional_pi_pulse_length':  52,
        'unconditional_pi_pulse_amp':      0, # updated by [rabi]
        'unconditional_pi2_pulse_length': 32,
        'unconditional_pi2_pulse_amp':     0, # updated by [rabi]
        'T1':                            6e3, # updated by [t1_qubit]
        'T2':                           13e3, # updated by [ramsey]
    },
    'readout': {
        'freq':   6.34,
        'power':  18,
        'length': 1000,
        'amp':    0.04
    },
    'twpa': {
        'freq':  5.788, # updated by [twpa]
        'power': 6      # updated by [twpa]
    },
    'averaging': 1_000,
    'flux': -0.065, # V
    
    ######## calibration-specific parameters ########
    
    'rabi_probe': {
        'npoints':      51,
        'max_amp':      0.4,
        'pulse_length': 1000
    },
    'rabi': {
        'npoints':                                     51,  # updated by [rabi_probe]
        'max_amp':                                     0.4,
        'unconditional_pi2_pulse_linearity_amp_limit': 0.31, # updated by [rabi_probe]
        'unconditional_pi_pulse_linearity_amp_limit':  0.24, # updated by [rabi_probe]
        'conditional_pi_pulse_linearity_amp_limit':    0.21  # updated by [rabi_probe]
    },
    'ramsey': {
        'long_ro_length': 1000,   # see $readout/length?
        'long_ro_amp':    0.04,   # see $readout/amp?
        'wait_min':       20,
        'wait_max':       30000,  # updated by [t1_qubit]: $ramsey/wait_max ← max($ramsey_wait_max, 5*T1)
        'npoints':        51,
        'averaging':      1_000,
        'width':          1.5e-3    # frequencies ← (freq-width/2, freq, freq+width/2)
    },
    'ramsey_t2': {
        'delta':          0.0     # $ramsey/freq - $qubit/freq in GHz
    },
    't1_qubit': {
        'num_t1':         8,     # wait_max will be adjusted to be greater or equal to $t1_qubit/num_t1 * T1
        'long_ro_length': 1000,  # see $readout/length?
        'long_ro_amp':    0.04,  # see $readout/amp?
        'wait_min':       20,
        'wait_max':       30000, # updated by [t1_qubit]
        'npoints':        51,
        'averaging':      1_000
    },
    'spectro_ro': {
        'averaging': 10_000
    },
    'spectro_qubit': {
        'averaging':           1_000,
        'coarse_pulse_length': 1500,
        'fine_pulse_length':   5000,
        'coarse_pulse_amp':    0.0075,
        'fine_pulse_amp':      0.00035,
        'coarse_sweep_width':  75,
        'fine_sweep_width':    25,
        'coarse_npoints':      51,
        'fine_npoints':        51
    }
    # 'default_path': 'F:/data/Qnode Fock_stab 3/calibrations',
    # 'filename': 'FILENAME', # {calib_id}_{calib_name}.h5
    # 'retries': 3,
    # 'qubit': {
    #     'freq':                        4.440, # updated by [ramsey], [spectro_qubit]
    #     'power':                          12,
    #     'conditional_pi_pulse_length':   700,
    #     'conditional_pi_pulse_amp':        0, # updated by [rabi]
    #     'unconditional_pi_pulse_length':  52,
    #     'unconditional_pi_pulse_amp':      0, # updated by [rabi]
    #     'unconditional_pi2_pulse_length': 32,
    #     'unconditional_pi2_pulse_amp':     0, # updated by [rabi]
    #     'T1':                            6e3, # updated by [t1_qubit]
    #     'T2':                           13e3, # updated by [ramsey]
    # },
    # 'readout': {
    #     'freq':   6.34,
    #     'power':  18,
    #     'length': 1000,
    #     'amp':    0.04
    # },
    # 'twpa': {
    #     'freq':  5.788, # updated by [twpa]
    #     'power': 6      # updated by [twpa]
    # },
    # 'averaging': 10_000,
    # 'flux': -0.065, # V
    
    # ######## calibration-specific parameters ########
    
    # 'rabi_probe': {
    #     'npoints':      201,
    #     'max_amp':      0.4,
    #     'pulse_length': 1000
    # },
    # 'rabi': {
    #     'npoints':                                     201,  # updated by [rabi_probe]
    #     'max_amp':                                     0.4,
    #     'unconditional_pi2_pulse_linearity_amp_limit': 0.31, # updated by [rabi_probe]
    #     'unconditional_pi_pulse_linearity_amp_limit':  0.24, # updated by [rabi_probe]
    #     'conditional_pi_pulse_linearity_amp_limit':    0.21  # updated by [rabi_probe]
    # },
    # 'ramsey': {
    #     'long_ro_length': 1000,   # see $readout/length?
    #     'long_ro_amp':    0.04,   # see $readout/amp?
    #     'wait_min':       20,
    #     'wait_max':       30000,  # updated by [t1_qubit]: $ramsey/wait_max ← max($ramsey_wait_max, 5*T1)
    #     'npoints':        201,
    #     'averaging':      10_000,
    #     'width':          1.5e-3    # frequencies ← (freq-width/2, freq, freq+width/2)
    # },
    # 'ramsey_t2': {
    #     'delta':          0.0     # $ramsey/freq - $qubit/freq in GHz
    # },
    # 't1_qubit': {
    #     'num_t1':         8,     # wait_max will be adjusted to be greater or equal to $t1_qubit/num_t1 * T1
    #     'long_ro_length': 1000,  # see $readout/length?
    #     'long_ro_amp':    0.04,  # see $readout/amp?
    #     'wait_min':       20,
    #     'wait_max':       30000, # updated by [t1_qubit]
    #     'npoints':        401,
    #     'averaging':      20_000
    # },
    # 'spectro_ro': {
    #     'averaging': 10_000
    # },
    # 'spectro_qubit': {
    #     'averaging':           20_000,
    #     'coarse_pulse_length': 1500,
    #     'fine_pulse_length':   5000,
    #     'coarse_pulse_amp':    0.0075,
    #     'fine_pulse_amp':      0.00035,
    #     'coarse_sweep_width':  75,
    #     'fine_sweep_width':    25,
    #     'coarse_npoints':      401,
    #     'fine_npoints':        401
    # }
}
