import re
import subprocess
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
    
    Args:
        src (`list` of `str`): lines of a given cell

    Returns:
        bool:
    """
    first_line = src[0].strip()
    return first_line[:3] != '#if' or eval(first_line[4:-1])

class DefaultCalibration:
    """
    Defines the code shared between all calibrations.
    
    Args:
        log (Log):
        report (Report):
        assumptions (dict):
        id (int):
        name (str):
        substitutions (dict):
        exopy_templ (str):
        pre (str): Log prefix
        
    Attributes:
        log:
        report:
        assumptions:
        id:
        name:
        substitutions:
        exopy_templ:
        pre:
        report_templ:
        results:
    """
    
    def __init__(self, log, report, assumptions, id, name, substitutions, exopy_templ, pre):
        self.log           = log
        self.report        = report
        self.assumptions   = assumptions
        self.id            = id
        self.name          = name
        self.substitutions = substitutions
        self.exopy_templ   = exopy_templ
        self.pre           = pre
        self.report_templ  = nbf.read(f'qualib/calibrations/{name}/template_{name}.ipynb', as_version=4).cells
        self.results       = {}
        return
    
    def handle_substitutions(self):
        """Handles substitutions. Should be called at the end of :py:func:`Calibration.handle_substitutions`.
        
        Returns:
            `None`
        """
        for key, val in self.substitutions.items():
            # Handle substitutions in exopy template
            self.exopy_templ = self.exopy_templ.replace(key, val)

            # Handle substitutions in report template
            for i in range(len(self.report_templ)):
                self.report_templ[i].source = self.report_templ[i].source.replace(key, val)
        return

    def pre_process(self, mapping):
        """Handles pre-placeholders. Should be called at the end of :py:func:`Calibration.pre_process`.

        Args:
            mapping (dict): Dictionary of ``'PRE_PLACEHOLDER': value`` pairs.
        
        Returns:
            `None`
        """
        return

    def post_process(self, mapping):
        """Handles post-placeholders. Should be called at the end of :py:func:`Calibration.post_process`.
        
        Args:
            mapping (dict): Dictionary of ``'POST_PLACEHOLDER': value`` pairs.
        
        Returns:
            `None`
        """
        self.log.info(self.pre, f'Handling post_process placeholders defined in "qualib/calibrations/{self.name}/{self.name}_utils.py"')
        self.log.info(self.pre, self.log.json(mapping))

        for key, val in mapping.items():
            for i, cell in enumerate(self.report.cells):
                self.report.cells[i]['source'] = cell['source'].replace(key, val)

        self.report.update()
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
        with open('qualib/calibrations/default_header.ipynb', encoding='utf8') as f:
            self.header = json.loads(f.read())['cells']
        for i in range(len(self.header)):
            self.header[i]['source'] = ''.join(self.header[i]['source'])

        self.notebook = nbfv4.new_notebook()
        self.filename = filename
        self.cells    = []

        self.assumptions_before = json.dumps(assumptions, indent=4)

        self.add_md_cell('# Calibration sequence')
        self.add_py_cell(calib_scheme_str.strip()+';')
        self.add_md_cell('# Assumptions before calibration sequence')
        self.add_py_cell(self.assumptions_before+';')

        self.add_md_cell('# Assumptions after calibration sequence')
        self.cell_aftr = len(self.cells)
        self.add_py_cell('')
        self.cell_diff = len(self.cells)
        self.add_md_cell('')
        
        for cell in self.header:
            if cell['cell_type'] == 'code':
                self.add_py_cell(cell['source'])
            if cell['cell_type'] == 'markdown':
                self.add_md_cell(cell['source'])

    def update(self):
        """Overwrites ``self.notebook`` and ``reports/report_TIMESTAMP.ipynb`` from the list of cells ``self.cells``.

        Returns:
            Report: ``self``.
        """
        self.notebook = nbfv4.new_notebook()

        for cell in self.cells:
            if cell['type'] == 'md':
                self.notebook['cells'].append(nbfv4.new_markdown_cell(cell['source']))
            if cell['type'] == 'py':
                self.notebook['cells'].append(nbfv4.new_code_cell(cell['source']))

        nbf.write(self.notebook, self.filename, version=4)
        return self
    
    def add_calibration(self, calibration):
        """Appends a calibration to the report.
        
        Args:
            calibration (Calibration): Instance of the current Calibration class.

        Returns:
            Report: ``self``.
        """
        for cell in calibration.report_templ:
            src = cell['source'].splitlines()
            if keep_cell(src): # Handle conditional cells
                if src[0][:3] == '#if':
                    src = src[1:]
                if cell['cell_type'] == 'code':
                    self.add_py_cell('\n'.join(src))
                if cell['cell_type'] == 'markdown':
                    self.add_md_cell('\n'.join(src))
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
        diff = [line for line in difflib.Differ().compare(befr, aftr) if line[0] in ('+', '-')]
        
        # Update assumptions after and assumptions diff
        self.cells[self.cell_aftr]['source'] = self.assumptions_after+';'
        self.cells[self.cell_diff]['source'] = ['# Assumptions diff\n\n', '```diff\n', *diff, '```']
        return self.update()

    def add_md_cell(self, src):
        self.cells.append({'type': 'md', 'source': src})
        return self.update()

    def add_py_cell(self, src):
        self.cells.append({'type': 'py', 'source': src})
        return self.update()

    def ins_md_cell(self, pos, src):
        self.cells.insert(pos, {'type': 'md', 'source': src})
        return self.update()

    def ins_py_cell(self, pos, src):
        self.cells.insert(pos, {'type': 'py', 'source': src})
        return self.update()