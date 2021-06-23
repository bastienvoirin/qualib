.. role:: py(code)
    :language: python

User guide
==================================

Flowchart
**********************************

.. graphviz::
    :align: center
    
    digraph G {
        rank = same;
        rankdir = LR;
        splines = true;
        esep = 1;
        node [
            shape = rect;
            fontname = "monospace";
        ];
        subgraph level_0 {
            run_all [
                label = "Qualib.run_all()";
            ];
        }
        subgraph level_1 {
            log_init [
                label = "Log.initialize()";
            ];
            report_init [
                label = "Report.__init__()";
            ];
            load_calib_scheme [
                label = "load_calibration_scheme()";
            ];
            load_assumptions [
                label = "load_assumptions()";
            ];
            run [
                label = "Qualib.run()";
            ];
        }
        subgraph level_2 {
            load_utils [
                label = "load_utils()";
            ];
            load_exopy_template [
                label = "load_exopy_template()";
            ];
            load_ipynb_template [
                label = "load_ipynb_template()";
            ];
            calib_init [
                label = "Calibration.__init__()";
            ];
            calib_handle_substitutions [
                label = "Calibration.handle_substitutions()";
                peripheries = 2;
            ];
            pre_process [
                label = "Calibration.pre_process()";
                peripheries = 2;
            ];
            report_add_calibration [
                label = "Report.add_calibration()";
            ];
            subprocess [
                label = "subprocess.run()";
            ];
            process [
                label = "Calibration.process()";
                peripheries = 2;
            ];
            post_process [
                label = "Calibration.post_process()";
                peripheries = 2;
            ];
            report_add_results [
                label = "Report.add_results()";
            ];
        }
        subgraph level_3 {
            handle_substitutions [
                label = "Handle substitutions";
                shape = plaintext;
                fontname = "sans-serif";
            ];
            handle_pre_placeholders [
                label = "Handle pre-placeholders";
                shape = plaintext;
                fontname = "sans-serif";
            ];
            handle_results [
                label = "Handle interfaces\nUpdate assumptions";
                shape = plaintext;
                fontname = "sans-serif";
            ];
            handle_post_placeholders [
                label = "Handle post-placeholders";
                shape = plaintext;
                fontname = "sans-serif";
            ];
            report_add_results_desc [
                label = "Update assumptions cells";
                shape = plaintext;
                fontname = "sans-serif";
            ];
        }
        run_all -> log_init;
        log_init -> report_init;
        report_init -> load_calib_scheme;
        load_calib_scheme -> load_assumptions;
        load_assumptions -> run;
        run -> load_utils;
        load_utils -> load_exopy_template;
        load_exopy_template -> load_ipynb_template;
        load_ipynb_template -> calib_init;
        calib_init -> calib_handle_substitutions;
        calib_handle_substitutions -> handle_substitutions [style = invis];
        calib_handle_substitutions -> pre_process;
        pre_process -> handle_pre_placeholders [style = invis];
        pre_process -> report_add_calibration;
        report_add_calibration -> subprocess;
        subprocess -> process;
        process -> handle_results [style = invis];
        process -> post_process;
        post_process -> handle_post_placeholders [style = invis];
        post_process -> report_add_results;
        report_add_results -> report_add_results_desc [style = invis];
        report_add_results:w -> run:s [constraint = false];
    }

Substitutions, placeholders and interfaces
******************************************

Substitutions
----------------------------------

A substitution is a mapping handled in :py:meth:`Calibration.handle_substitutions`, before any placeholder. Substitutions are typically used to define several variants of a given calibration. Substitutions can be found in:

    * ``CALIBRATION_NAME_template.meas.ini`` (format: ``SUBSTITUTION``)
    * ``template_CALIBRATION_NAME.ipynb`` (format: ``{SUBSTITUTION}``)

A substitution can be:

    * Implicit: hardcoded, "auto"
    * Explicit: user-defined in ``calibration_scheme.py``, "user".

.. note::
    Special substitutions:
    
        * [auto] ``{HDF5_PATH}`` in ``template_CALIBRATION_NAME.ipynb``: absolute path to the HDF5 data file; replaced with ``default_path`` (defined in ``assumptions.py``) and a timestamp.
        * [user] ``{NAME}`` in ``calibration_scheme.py``: name of the substitutions group, in *camel\_case*.
    
Pre-placeholders
----------------------------------

Pre-placeholders can be found in:

    * ``CALIBRATION_NAME_template.meas.ini`` (format: ``$parameter`` or ``$section/parameter``) where ``section`` and ``parameter`` are alphanumeric strings (``a``-``z``, ``A``-``Z``, ``0``-``9``, ``_``)
    * ``template_CALIBRATION_NAME.ipynb`` (format: ``{PRE_PLACEHOLDER}``)
    
Pre-placeholders are handled in ``Calibration.pre_process()``.

Post-placeholders
----------------------------------

Post-placeholders can be found in:

    * ``template_CALIBRATION_NAME.ipynb`` (format: ``{POST_PLACEHOLDER}``)
    
Post-placeholders are handled in ``Calibration.post_process()``.
        
Interfaces
----------------------------------

An interface is a special Python variable defined in ``template_CALIBRATION_NAME.ipynb`` whose value is fetched and processed by ``Calibration.process()`` (at ``CALIBRATION_NAME_utils.py``) and/or ``DefaultCalibration.process()`` (at ``calibrations/default.py``). Currently, there are 4 interfaces:

.. list-table:: List of interfaces currently supported
    :widths: 10 90
    :header-rows: 1

    *   - Interface
        - Description
    *   - ``_results``
        - ``dict`` of ``name: value`` pairs summarizing the calibration results  
    *   - ``_err``
        - ``dict`` of ``error_message: condition_to_throw`` pairs defining custom runtime errors (for instance to detect whether a curve fit failed or not)
    *   - ``_opt``
        - ``list``, ``tuple``, or ``numpy.ndarray`` of optimized parameters, typically returned by ``scipy.optimize.curve_fit()``
    *   - ``_cov``
        - ``list``, ``tuple``, or ``numpy.ndarray`` of covariance arrays, typically returned by ``scipy.optimize.curve_fit()``
        
Calibration sequences
**********************************

assumptions.py
----------------------------------

``assumptions.py`` should be a Python dictionary or depth 1 or 2.

calibration_scheme.py
----------------------------------

``calibration_scheme.py`` should be a Python list. Each element of this list specifies a calibration to run.

Format:

.. code-block:: py
    
    [
        {"name": "a_calibration"},

        {"name": "another_calibration",
         "substitutions": {"NAME":                "variant_in_camel_case",
                           "A_SUBSTITUTION":      "a_value",
                           "ANOTHER_SUBTITUTION": "another_value"}}
    ]

* ``name``: the calibration name
* ``substitutions``: an optional dictionary of substitutions; if present, ``NAME`` must be defined.

Calibrations
**********************************

template.ipynb
----------------------------------

Typical ``template.ipynb``
++++++++++++++++++++++++++++++++++

.. nbinput:: md
    
    # Calibration name (SUBSTITUTION)
    ## Result: $POST_PLACEHOLDER$ unit

.. nbinput:: ipython3
    
    # load experimental data
    file = h5py.File(HDF5_PATH, 'r', swmr=True)
    xdata = file['data']['x'][()]
    ydata = file['data']['y'][()];

.. nbinput:: ipython3
    
    # fit experimental data
    popt, pcov = opt.curve_fit(function, xdata, ydata, guesses=(0, 1, 2))
    f'a, b, c = {popt}'

.. nbinput:: ipython3
    
    # plot experimental data and curve fit(s)
    fig, ax = plt.subplots()
    ax.plot(xdata, ydata, '.-', label='Data')
    ax.plot(xdata, function(xdata, *popt), label=f'Fit: a = {popt[0]:f}')
    ax.legend();

.. nbinput:: ipython3
    
    # optional interfaces: raises an exception when any(np.sqrt(np.diag(_cov)) >= 0.05*_opt)
    # where np.sqrt(np.diag(_cov)) gives the standard deviation on the optimized parameters
    _opt = popt
    _cov = pcov

    # optional interface: raises an exception when a specific condition is met
    _err = {'Custom error', _opt[0] < 0}

    # mandatory interface
    _results = {'a': popt[0]}
    _results

|
| This Jupyter notebook should be saved as ``calib_name_template.ipynb`` under ``qualib/calibrations/calib_name``.

Conditional code cells
++++++++++++++++++++++++++++++++++

One can specify under which condition(s) a given code cell is passed to the report generator. For instance, analysis code can be chosen from several options using a substitution. The first line of a conditional code cell is a commented `if` statement, for exemple:

.. nbinput::ipython3

    #if 
