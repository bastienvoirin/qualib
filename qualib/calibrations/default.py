import re
import nbformat as nbf
import nbformat.v4 as nbfv4
import json
import numpy as np
import scipy
import difflib
import sys
import os

def keep_cell(src):
    """Handles conditional cells: skips a given cell if its first line is ``#if condition:`` and ``condition`` evaluates to ``False``.
    
    """
    first_line = src[0].strip()
    if first_line[:3] != '#if' or eval(first_line[4:-1]):
        return src[1:]
    return []

class DefaultCalibration:
    """
    Defines the code shared between all calibrations.
    
    Args:
        log (Log):
        report (Report):
        calib_id (int):
        calib_name (str):
        
    Attributes:
        cells (list):
    """
    
    def __init__(self, log, report, calib_id, calib_name):
        return
    
    def handle_substitutions(self, log, report, subs_name, subs_misc):
        """Handles substitutions. Should be called at the end of :py:func:`Calibration.handle_substitutions`.
        
        Args:
            log (Log):
            report (Report):
            subs_name (str):
            subs_misc (dict):
        """
        return

    def pre_process(self, log, report):
        """Handles pre-placeholders. Should be called at the end of :py:func:`Calibration.pre_process`.

        :param Log log:
        :param Report report:
        :return: None
        """
        return

    def post_process(self, log, report, calib_name, mapping):
        """Handles post-placeholders. Should be called at the end of :py:func:`Calibration.post_process`.

        :param Log log:
        :param Report report:
        :param str calib_name:
        :param dict mapping: Dictionary of ``'POST_PLACEHOLDER': value`` pairs.
        :return: None
        """
        log.info(f'{self.pre} Handling post_process placeholders defined in "qualib/calibrations/{calib_name}/{calib_name}_utils.py"')
        log.info(log.json(mapping))

        for key, val in mapping.items():
            for i, cell in enumerate(report.cells):
                report.cells[i]['source'] = cell['source'].replace(key, val)

        report.update()
        return

######################################################################

class Report:
    """Generates and updates a Jupyter notebook to report the calibrations results.
        
    Args:
        filename (str): Report filename.
        assumptions (dict): State of the assumptions before the calibrations.
        calib_scheme_str (str): String representation of the calibration sequence.
            
    Attributes:
        header (list): List of cells defined in ``qualib/calibrations/default_header.py``.
        filename (str):
        cells (list):
        notebook:
        assumptions_before (str):
        assumptions_after (str):
    """
        
    def __init__(self, filename, assumptions, calib_scheme_str):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open('qualib/calibrations/default_header.ipynb') as f:
            self.header = json.loads(f.read())['cells']
        self.notebook = nbfv4.new_notebook()
        self.filename = filename
        self.cells    = []

        self.assumptions_before = json.dumps(assumptions, indent=4)

        self.add_md_cell('# Calibration sequence')
        self.add_py_cell(calib_scheme_str.strip()+';')
        self.add_md_cell('# Assumptions before calibration sequence')
        self.add_py_cell(self.assumptions_before+';')
        
        for cell in self.header:
            if cell['cell_type'] == 'py':
                self.add_py_cell(''.join(cell['source']))
            if cell['cell_type'] == 'md':
                self.add_md_cell(''.join(cell['source']))

        self.update()

    def update(self):
        """Overwrites ``self.notebook`` from the list of cells ``self.cells``.

        Returns:
            Report: ``self``.
        """
        self.notebook = nbfv4.new_notebook()

        for cell in self.cells:
            if cell['type'] == 'md':
                nbfv4.new_markdown_cell(cell['source'])
            if cell['type'] == 'py':
                nbfv4.new_code_cell(cell['source'])

        with open(self.filename, 'w') as f:
            nbf.write(self.notebook, f)
        return self
    
    def add_calibration(self):
        """Appends a calibration to the report.
        
        Returns:
            Report: ``self``.
        """
        return self
        
    def add_results(self, assumptions):
        """Reports results from the previous calibration.
        
        Args:
            assumptions (dict): Dictionary of assumptions.
            
        Returns:
            Report: ``self``.
        """
        self.assumptions_after = json.dumps(assumptions, indent=4)
        befr = self.assumptions_before.splitlines(keepends=True)
        aftr = self.assumptions_after.splitlines(keepends=True)
        diff = [line for line in difflib.Differ().compare(befr, aftr) if line[0] != ' ']
        
        # Add assumptions after and assumptions diff
        for i, cell in enumerate(self.cells):
            if cell['type'] == 'md' and cell['source'][0] == '# Assumptions before calibration sequence':
                self.ins_md_cell(i+2, ['# Assumptions after calibration sequence'])
                self.ins_py_cell(i+3, (self.assumptions_after+';').splitlines(keepends=True))
                self.ins_md_cell(i+4, ['# Assumptions diff\n\n', '```diff\n', *diff, '```'])
                break

        return self.write()

    def add_md_cell(self, src):
        """Appends a Markdown cell to the report.

        Args:
            src (str): Raw content of the Markdown cell.
        
        Returns:
            Report: ``self``.
        """
        self.cells.append({'type': 'md', 'source': src})
        return self.update()

    def add_py_cell(self, src):
        """Appends a Python cell to the report.
        
        Args:
            src (str): Raw content of the Python cell.
        
        Returns:
            Report: ``self``.
        """
        self.cells.append({'type': 'py', 'source': src})
        return self.update()

    def ins_md_cell(self, pos, src):
        """Inserts a Markdown cell in the report.
        
        Args:
            pos (int): Position of the new Markdown cell.
            src (str): Source code of the new Markdown cell.
        
        Returns:
            Report: ``self``.
        """
        self.cells.insert(pos, {
            'cell_type': 'markdown',
            'metadata':  {},
            'source':    src
        })
        return self.update()

    def ins_py_cell(self, pos, src):
        """Inserts a Python cell in the report.
        
        Args:
            pos (int): Position of the new Python cell.
            src (str): Source code of the new Python cell.
        
        Returns:
            Report: ``self``.
        """
        self.cells.insert(pos, {
            'cell_type':       'code',
            'execution_count': None,
            'metadata':        {},
            'outputs':         [],
            'source':          src
        })
        return self.update()