.. role:: py(code)
    :language: python

Reference
==================================

Substitutions, placeholders and interfaces
******************************************

Substitutions
----------------------------------

A substitution is a placeholder which is handled early, in ``Calibration.pre_process()``. Substitutions are used to define several variants of a given calibration. Substitutions can be found in:

    * ``CALIBRATION_NAME_template.meas.ini`` (format: ``SUBSTITUTION``)
    * ``template_CALIBRATION_NAME.ipynb`` (format: ``SUBSTITUTION``)

A substitution can be:

    * Implicit: hardcoded, "auto"
    * Explicit: user-defined in ``calibration_scheme.py``, "user".

.. note::
    Special substitutions:
    
        * [auto] ``HDF5_PATH`` in ``template_CALIBRATION_NAME.ipynb``: absolute path to the HDF5 data file; replaced during ``DefaultCalibration.pre_process()`` with ``default_path`` (defined in ``assumptions.py``) and a timestamp.
        * [user] ``NAME`` in ``calibration_scheme.py``: name of the substitutions group, in *camel\_case*.
    
Placeholders
----------------------------------

Placeholders can be found in:

    * ``CALIBRATION_NAME_template.meas.ini`` (format: ``$parameter`` or ``$section/parameter``)
    * ``template_CALIBRATION_NAME.ipynb`` (format: ``PLACEHOLDER``)
    
Placeholders are handled in ``Calibration.pre_process()``.
        
Interfaces
----------------------------------

An interface is a special Python variable defined in ``template_CALIBRATION_NAME.ipynb`` whose value is fetched and processed by ``Calibration.process()`` (at ``CALIBRATION_NAME_utils.py``) and ``DefaultCalibration.process()`` (at ``calibrations/default.py``). Currently, there are 4 interfaces:

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
        
Flowchart
**********************************

.. graphviz::
    
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
                pos="0,0!";
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
            calibration [
                label = "Calibration.__init__()";
            ];
            pre_process [
                label = "Calibration.pre_process()";
            ];
            invis_1 [
                style = invis;
            ];
            subprocess [
                label = "subprocess.run()";
            ];
            calib_process [
                label = "Calibration.process()";
            ];
            invis_2 [
                style = invis;
            ];
            post_process [
                label = "Calibration.post_process()";
            ];
        }
        subgraph level_3 {
            calib_substitutions [
                label = "Handle substitutions";
                shape = oval;
            ];
            calib_placeholders [
                label = "Handle placeholders";
                shape = oval;
            ];
        }
        run_all -> log_init;
        log_init -> load_calib_scheme;
        load_calib_scheme -> load_assumptions;
        load_assumptions -> run;
        run -> load_utils;
        load_utils -> load_exopy_template;
        load_exopy_template -> calibration;
        calibration -> pre_process;
        pre_process:e -> calib_substitutions:n;
        calib_substitutions:s -> subprocess:e;
        subprocess -> calib_process;
        calib_process:e -> calib_placeholders:n;
        calib_placeholders:s -> post_process:e;
        post_process:w -> run:s [constraint = false];
        pre_process -> invis_1 [style = invis];
        invis_1 -> subprocess [style = invis];
        calib_process -> invis_2 [style = invis];
        invis_2 -> post_process [style = invis];
    }

Calibration sequences
**********************************

assumptions.py
----------------------------------

``assumptions.py`` should be a Python dictionary.

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

utils.py
----------------------------------

``Calibration`` inherits from, and overrides, ``DefaultCalibration``.

qualib/
**********************************

log.py
----------------------------------

.. py:class:: Log
    
    Keyword arguments ``**kwargs`` are not supported yet, but may be added in future versions.
    
    .. py:method:: initialize(timestamp, max_label_len=5)
        
        Defines the path and filename of the log from a ``timestamp`` string (``logs/{timestamp}.log``) as well as the indentation needed to align log entries. ``max_label_len`` is set to ``5`` by default to align ``info``, ``debug``, ``warn`` and ``error`` messages. Set ``max_label_len`` to ``0`` or a negative integer to disable alignment.
    
    .. py:method:: info(*args, **kwargs)
        
        Calls ``log('info', *args, **kwargs)``.
    
    .. py:method:: debug(*args, **kwargs)
    
        Calls ``log('debug', *args, **kwargs)``.
    
    .. py:method:: warn(*args, **kwargs)
        
        Calls ``log('warn', *args, **kwargs)``.
    
    .. py:method:: error(*args, **kwargs)
        
        Calls ``log('error', *args, **kwargs)``.
    
    .. py:method:: exc()
        
        Logs the current exception traceback with an ``[ERROR]`` label.
    
    .. py:method:: log(label, *args, **kwargs)
        
        Logs its arguments. Multiples lines may be passed to this method
        
        * As a list: ``log(label, lines)``, `e.g.` ``log('info', [line1, line2, line3])``
        * As multiple arguments: ``log(label, *lines)``, `e.g.` ``log('info', line1, line2, line3)``
    
    .. py:method:: json(obj)
    
load.py
----------------------------------

.. py:function:: load_calibration_scheme(log, path)
    
    Loads, evaluates and returns the calibration sequence found at ``path`` as a list, logging to ``log`` instance of :py:class:`Log`.
    
.. py:function:: load_assumptions(log)
    
    Loads, evaluates and returns ``assumptions.py`` as a dictionary, logging to ``log`` instance of :py:class:`Log`.
    
.. py:function:: load_exopy_template(log, calib, sub)
    
    Reads the Exopy measurement template found at ``qualib/calibrations/{calib}/{calib}_template.meas.ini``, logging to ``log`` instance of :py:class:`Log`.
    
.. py:function:: load_utils(log, calib, sub)
    
    Imports and returns Calibration class from ``qualib/calibrations/{calib}/{calib}_utils.py``, logging to ``log`` instance of :py:class:`Log`.

main.py
----------------------------------

.. py:class:: Qualib
    
    Wrapper supclass.
    
    .. py:method:: run(calib_id, calib_name, sub_name, sub_repl, report_filename, timestamp, assumptions)
        
        Runs a calibration.
    
    .. py:method:: run_all(pkg_calib_scheme)
        
        Runs a calibration sequence whose path is either passed as ``pkg_calib_scheme`` (package usage) or in ``sys.argv`` (CLI/module usage).

reports/
**********************************

Each report consists in:

    * Assumptions before calibration sequence
    * Assumptions after calibration sequence
    * Assumptions diff
    * Report header (imports, utility functions)
    * Calibrations reports

logs/
**********************************

Logs consist in timestamped and labeled lines of information ('info'), debug informations ('debug'), warning ('warn'), errors ('error') and/or custom content.
