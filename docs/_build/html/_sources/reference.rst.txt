.. role:: py(code)
    :language: python

Reference
==================================

qualib/
**********************************

log.py
----------------------------------

.. automodule:: qualib.log
    
load.py
----------------------------------

.. automodule:: qualib.load

main.py
----------------------------------

.. automodule:: qualib.main

calibrations/default.py
----------------------------------

.. automodule:: qualib.calibrations.default

qualib/calibrations/NAME/
*************************************

NAME_utils.py
----------------------------------

.. py:class:: qualib.calibrations.NAME.NAME_utils.Calibration
    
    Inherits from, and overrides, :py:class:`qualib.calibrations.default.DefaultCalibration`.

    .. py:method:: handle_substitutions

    .. py:method:: pre_process

    .. py:method:: process

    .. py:method:: post_process

reports/
**********************************

Each report consists in:

    * Calibration sequence (:py:meth:`Report.__init__()<Report>`)
    * Assumptions before calibration sequence (:py:meth:`Report.__init__()<Report>`)
    * Assumptions after calibration sequence (:py:meth:`Report.add_results()`)
    * Assumptions diff (:py:meth:`Report.add_results()`)
    * Report header (imports, utility functions) (:py:meth:`Report.__init__()<Report>`)
    * Calibrations reports (:py:meth:`Report.add_calibration()`, :py:meth:`Report.add_results()`)

logs/
**********************************

Logs consist in timestamped and labeled lines of information ("info"), debug information ("debug"), warning ("warn"), errors ("error") and/or custom content.
