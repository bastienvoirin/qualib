Getting started
==================================

Defining a calibration
**********************************

Exopy template
----------------------------------

Typical usage:

* Set ``default_path = $my_default_path`` in ``calib_name_template.meas.ini`` and define ``my_default_path`` value in ``assumptions.py``

Jupyter notebook template
----------------------------------

.. nbinput:: md
    
    # Calibration name (§TYPE§)
    ## §PLACEHOLDER§

.. nbinput:: ipython3
    
    file = h5py.File(HDF5_PATH, 'r', swmr=True)
    xdata = file['data']['x'][()]
    ydata = file['data']['y'][()]

.. nbinput:: ipython3
    
    popt, pcov = opt.curve_fit(function, xdata, ydata, guesses=(0, 1, 2))
    f'a, b, c = {popt}'

.. nbinput:: ipython3
    
    fig, ax = plt.subplots()
    ax.plot(xdata, ydata, '.-', label='Data')
    ax.plot(xdata, function(xdata, *popt), label=f'Fit: a = {popt[0]:f}')
    ax.legend();

.. nbinput:: ipython3
    
    _opt = popt
    _cov = pcov
    _err = {'Custom error', _opt[0] < 0}
    _results = {'a': popt[0]}
    _results

|
| This Jupyter notebook should be saved as ``calib_name_template.ipynb`` under ``qualib/calibrations/calib_name``.

Python script
----------------------------------

Defining a calibration sequence
**********************************

Example:

.. code-block:: py
    
    [
        {"name": "spectro_ro",
         "substitutions": {"NAME": "phase_only",
                           "TYPE": "phase only"}},
         
        {"name": "spectro_ro",
         "substitutions": {"NAME": "circle_fit",
                           "TYPE": "circle fit"}},
                           
        {"name": "spectro_qubit"},
        
        {"name": "rabi_probe"},
        
        {"name": "rabi",
         "substitutions": {"NAME":  "uncond_pi2",
                           "PULSE": "unconditional_pi2_pulse",
                           "TYPE":  "unconditional pi/2 pulse"}},
                           
        {"name": "rabi",
         "substitutions": {"NAME":  "uncond_pi",
                           "PULSE": "unconditional_pi_pulse",
                           "TYPE":  "unconditional pi pulse"}},
                           
        {"name": "rabi",
         "substitutions": {"NAME":  "cond_pi",
                           "PULSE": "conditional_pi_pulse",
                           "TYPE":  "conditional pi pulse"}},
                           
        {"name": "ramsey"},
        
        {"name": "t1_qubit"}
    ]

Installation/usage
**********************************

CLI/module usage
----------------------------------

* First, get Qualib locally from https://github.com/bastienvoirin/qualib.git
* Then, open a terminal and run

.. code-block:: sh
    
    python -m qualib.main calibration_scheme.py


Package usage
----------------------------------

.. code-block:: sh
    
    pip install qualib

.. code-block:: py
    
    from qualib.main import Qualib
    
    qualib = Qualib()
    qualib.run_all('calibration_scheme.py')

