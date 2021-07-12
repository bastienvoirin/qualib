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
    
    # Calibration name ({TYPE})
    ## {PLACEHOLDER}

.. nbinput:: ipython3
    
    file = h5py.File('HDF5_PATH', 'r', swmr=True)
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
    
    # optional
    _opt = popt
    _cov = pcov
    
    # optional
    _err = {'Custom error', _opt[0] < 0}
    
    # mandatory
    _results = {'a': popt[0]}
    _results

|
| This Jupyter notebook should be saved as ``calib_name_template.ipynb`` under ``qualib/calibrations/calib_name``.

Python script
----------------------------------

Template:

.. literalinclude:: literalinclude/calib_utils.py
    :language: python

Example ("Rabi" calibration):

.. literalinclude:: literalinclude/rabi_utils.py
    :language: python

Defining a calibration sequence
**********************************

Example:

.. literalinclude:: literalinclude/calib_scheme_example.py
    :language: python

Installation/usage
**********************************

CLI/module usage
----------------------------------

* First, install Qualib locally from https://github.com/bastienvoirin/qualib.git
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

