.. role:: py(code)
    :language: python

Reference
==================================

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
            subprocess [
                label = "subprocess.run()";
            ];
            calib_process [
                label = "Calibration.process()";
            ];
            post_process [
                label = "Calibration.post_process()";
            ];
            loop [
                label = "Loop?";
                shape = diamond;
            ];
        }
        subgraph level_3 {
            calib_init_substitutions [
                label = "Handle substitutions\nin Exopy template";
                shape = oval;
            ];
            calib_init_placeholders [
                label = "Handle placeholders\nin Exopy template";
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
        calibration -> calib_init_substitutions;
        calib_init_substitutions -> calib_init_placeholders;
        calib_init_placeholders:w -> pre_process:e
        pre_process -> subprocess;
        subprocess -> calib_process;
        calib_process -> post_process;
        post_process -> loop;
        loop:w -> run:s [constraint = false];
    }

assumptions.py
**********************************

``assumptions.py`` should be a Python dictionary.

calibration_scheme.py
**********************************

``assumptions.py`` should be a Python list. Each element of this list specifies a calibration to run.

Format:

.. code-block:: py
    
    [
        {"name": "calib_name_0"},
        {"name": "calib_name_1", "substitutions": [{"name": "variant",
                                                    "repl": {"PLACEHOLDER_A": "value_A",
                                                             "PLACEHOLDER_B": "value_B"}}]},
        {"name": "calib_name_2", "substitutions": [{"name": "variant_0",
                                                    "repl": {"PLACEHOLDER_A": "value_A_0",
                                                             "PLACEHOLDER_B": "value_B_0"}},
                                                   {"name": "variant_1",
                                                    "repl": {"PLACEHOLDER_0": "value_A_1",
                                                             "PLACEHOLDER_1": "value_B_1"}}]}
    ]

* ``name``: the calibration name
* ``substitutions``: a list of substitution groups, Python dictionaries with the following keys:

    * ``name``: the name of this substitution group
    * ``repl``: a dictionary of ``"PLACEHOLDER": "value"`` pairs

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
