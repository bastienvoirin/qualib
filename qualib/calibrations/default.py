from __future__ import annotations
import re
import subprocess
import nbformat as nb
from nbformat.v4 import new_notebook
from nbformat.v4 import new_markdown_cell as new_md_cell
from nbformat.v4 import new_code_cell as new_py_cell
import json
import numpy as np
import scipy
import difflib
import sys
import os
from typing import List, Dict, Generator
from ..log import Log

def get_diff(prev: List[str], next: List[str]) -> Generator[str, None, None]:
    """Generator of diff lines between ``prev`` and ``next``.
    
    Args:
        prev: First list of lines.
        next: Second list of lines.
    """
    return (line for line in difflib.Differ().compare(prev, next)
            if line[0] in ('+', '-'))

def keep_cell(src: List[str]) -> bool:
    """
    Handles conditional cells: skips a given cell if its first line is
    ``#if condition:`` and ``condition`` evaluates to ``False``.
    
    Args:
        src: Lines of a given cell.
    """
    first_line = src[0].strip()
    return first_line[:3] != '#if' or eval(first_line[4:-1])

def handle_magic_commands(log: Log, pre: str, line: str) -> bool:
    """Filters magic commands and runs ``%run path_or_url`` ones.
    
    Args:
        log: Logging object.
        pre: Optional log entry prefix.
        line: Line to process.
        
    Returns:
        ``False`` if ``line`` is a magic command, ``True`` otherwise.
    """
    if line[0][:4] == r'%run':
        # TODO: Execute script at specified URL
        log.debug(pre, line)
    return line[0] != '%'

######################################################################

class DefaultCalibration:
    """
    Defines the code shared between all calibrations.
    
    Args:
        log (Log): Logging object.
        report (Report): Default report object.
        assumptions (dict): Current state of the assumptions
                            (updated after each calibration).
        id (int): Natural number giving the rank of the calibration to run.
        name (str): Name of the calibration to run (in lowercase).
        substitutions (dict): Dictionary of substitutions.
        exopy_templ (str): Content of the Exopy measurement template.
        pre (str): Default prefix for log entries.
        timestamp (str): Timestamp used to create the log and report files.
        
    Attributes:
        log (Log): Logging object.
        report (Report): Default report object.
        assumptions (dict): Current state of the assumptions
                            (updated after each calibration).
        id (int): Natural number giving the rank of the calibration to run.
        name (str): Name of the calibration to run (in lowercase).
        substitutions (dict): Dictionary of substitutions.
        exopy_templ (str):
        pre (str): Default prefix for log entries.
        timestamp (str): Timestamp used to create the log and report files.
        report_templ (list): Cells of the calibration report template.
        hdf5_path (str): Relative path to the HDF5 measurement file.
        results (dict): Dictionary of results.
    """
    
    def __init__(self, log: Log, report: Report, assumptions: dict, id: int,
                 name: str, substitutions: Dict[str, str], exopy_templ: str,
                 pre: str, timestamp: str):
        self.log           = log
        self.report        = report
        self.assumptions   = assumptions
        self.id            = id
        self.name          = name
        self.substitutions = substitutions
        self.exopy_templ   = exopy_templ
        self.pre           = pre
        self.timestamp     = timestamp

        self.report_templ  = nb.read(f'qualib/calibrations/{name}/template_{name}.ipynb', as_version=4).cells
        self.hdf5_path     = f'{assumptions["default_path"]}/{timestamp}_{id:03d}_{pre[:-1]}.h5'
        self.results       = {}
    
    def handle_substitutions(self, mapping: Dict[str, str] = {}) -> None:
        """Handles substitutions. Should be called at the
        end of :py:func:`Calibration.handle_substitutions`.
        
        Args:
            mapping: Dictionary of substitutions.
        """
        mapping['HDF5_PATH'] = self.hdf5_path
        for key, val in {**mapping, **self.substitutions.items()}:
            # Handle substitutions in Exopy template
            self.exopy_templ = self.exopy_templ.replace(key, val)

            # Handle substitutions in report template
            for i in range(len(self.report_templ)):
                self.report_templ[i].source = self.report_templ[i].source.replace('{'+key+'}', val)

    def pre_process(self, mapping: Dict[str, str] = {}) -> None:
        """Handles pre-placeholders. Should be called at
        the end of :py:func:`Calibration.pre_process`.

        Args:
            mapping: Dictionary of ``'PRE_PLACEHOLDER': value`` pairs.
        """
        # Handle pre-placeholders in Exopy template
        exopy_templ_befr = self.exopy_templ.splitlines()
        pre_placeholders = re.findall(r'(\$([a-z0-9_]+)(?:/([a-z0-9_]+))?)',
                                      self.exopy_templ,
                                      re.MULTILINE)
        for tree, root, leaf in pre_placeholders:
            self.log.debug(self.pre, str((tree, root, leaf)))
            if leaf:
                # Replace $section/parameter with assumptions[section][parameter]
                self.exopy_templ = self.exopy_templ.replace(tree, str(self.assumptions[root][leaf]))
            else:
                # Replace $parameter with assumptions[parameter]
                self.exopy_templ = self.exopy_templ.replace(tree, str(self.assumptions[root]))
        self.exopy_templ = self.exopy_templ.replace(self.assumptions['filename'], self.hdf5_path)
        exopy_templ_aftr = self.exopy_templ.splitlines()
        for line in get_diff(exopy_templ_befr, exopy_templ_aftr):
            # Remove unnecessary whitespaces and log exopy_templ diff
            self.log.debug(self.pre, f'{line[0]} {line[1:].strip()}')

        # Generating NAME.meas.ini file
        meas_path = f'qualib/calibrations/{self.name}/{self.name}.meas.ini'
        self.log.info(self.pre, f'Generating "{meas_path}"')
        with open(meas_path, 'w', encoding='utf-8') as f:
            f.write(self.exopy_templ)

        # Handle pre-placeholders in report template
        for key, val in mapping.items():
            for i in range(len(self.report_templ)):
                self.report_templ[i]['source'] = self.report_templ[i]['source'].replace('{'+key+'}', val)

    def process(self) -> None:
        """Executes analysis code and updates assumptions.

        """
        self.log.info(self.pre, 'Adding final conditional cells ("#if condition and \'STATUS\' == \'done\'")')
        for i, cell in enumerate(self.report_templ):
            src = cell['source'].splitlines()
            if keep_cell(src):
                self.report.cells.pop()
            self.report_templ[i]['source'] = self.report_templ[i]['source'].replace('STATE', 'done')
        self.report.add_calibration(self)

        self.log.info(self.pre, 'Executing header')
        for cell in self.report.header:
            if cell['cell_type'] == 'code':
                # Handle magic commands
                code = '\n'.join([
                    line for line in cell['source'].splitlines()
                    if handle_magic_commands(self.log, self.pre, line)
                ])
                
                # Execute code cell
                try:
                    exec(code, globals(), locals())
                except:
                    self.log.debug('', code.splitlines())
                    raise

        self.log.info(self.pre, f'Executing "qualib/calibrations/{self.name}/template_{self.name}.ipynb" code cells')
        loc = locals()
        for cell in self.report.cells[self.report.last_calibration:]:
            if cell['type'] == 'py':
                # Execute code cell
                try:
                    exec(cell['source'], loc, loc)
                except:
                    self.log.debug('', cell['source'].splitlines())
                    raise
                
                # Fetch results
                if '_results' in loc and '_results' in cell['source']:
                    self.log.info(self.pre, 'Fetching results')
                    self.results = loc['_results']

                # Check standard deviations against optimized values
                if '_opt' in loc and '_cov' in loc and '_opt' in cell['source'] and '_cov' in cell['source']:
                    self.log.info(self.pre, 'Checking standard deviations against optimized values')
                    ratios  = np.sqrt(np.diag(loc['_cov'])) / np.abs(loc['_opt'])
                    failed  = ', '.join([f'_opt[{ind}]' for ind in np.where(ratios > 0.05)[0]])
                    message = f'Standard deviation too large for {failed}\n'\
                              f'  If a parameter is not relevant, exclude it '\
                              f'from _opt and _cov in template_{self.name}.ipynb'
                    assert all(ratios <= 0.05), (self.log.error(self.pre, message) and False) or message
                    
                # Handle user-defined errors
                if '_err' in loc and '_err' in cell['source']:
                    self.log.info(self.pre, 'Handling custom errors')
                    errors = []
                    for message, condition in loc['_err'].items():
                        if condition:
                            errors.append(message)
                            self.log.error(self.pre, message)
                    assert not errors, '\n  '+'\n  '.join(errors)

    def post_process(self, mapping: Dict[str, str] = {}) -> None:
        """Handles post-placeholders. Should be called at
        the end of :py:func:`Calibration.post_process`.
        
        Args:
            mapping: Dictionary of ``'POST_PLACEHOLDER': value`` pairs.
        """
        self.log.info(self.pre, f'Handling post_process placeholders defined in "qualib/calibrations/{self.name}/{self.name}_utils.py"')
        self.log.info(self.pre, self.log.json(mapping))

        for key, val in mapping.items():
            for i in range(len(self.report.cells)):
                src = self.report.cells[i]['source']
                if type(src) == list:
                    src = '\n'.join(src)
                self.report.cells[i]['source'] = src.replace(key, val)

        self.report.update()

######################################################################

class Report:
    """Generates and updates a Jupyter notebook to report the calibrations results.
        
    Args:
        filename (str):
        assumptions (dict): Dictionary of assumptions.
        calib_scheme_str (str):
            
    Attributes:
        log (Log): Logging object.
        filename (str):
        header (list):
        notebook:
        cells (list):
        assumptions (dict):
        assump_befr (str):
        assump_aftr (str):
        cell_befr (int):
        cell_aftr (int):
    """
    
    def __init__(self, log: Log, filename: str, assumptions: dict, calib_scheme: str):
        self.log         = log
        self.filename    = filename
        self.assumptions = dict(assumptions)
        self.assump_befr = json.dumps(assumptions, indent=4)
        self.header      = nb.read('qualib/calibrations/default_header.ipynb', as_version=4).cells
        self.notebook    = new_notebook()
        self.cells       = []

        self.add_md_cell('# Calibration sequence')
        self.add_py_cell(calib_scheme.strip()+';')
        self.add_md_cell('# Assumptions before calibration sequence')
        self.add_py_cell(self.assump_befr+';')

        self.add_md_cell('# Assumptions after calibration sequence')
        self.cell_aftr: int = len(self.cells) # Placeholder cell
        self.add_py_cell('')
        self.cell_diff: int = len(self.cells) # Placeholder cell
        self.add_md_cell('# Assumptions diff')
        
        # Add default header (imports and useful functions)
        for cell in self.header:
            if cell['cell_type'] == 'code':
                self.add_py_cell(cell['source'])
            if cell['cell_type'] == 'markdown':
                self.add_md_cell(cell['source'])

    def update(self) -> Report:
        """Overwrites ``self.notebook`` and ``reports/report_TIMESTAMP.ipynb``
        from the list of cells ``self.cells``.
        
        """
        self.notebook = new_notebook()

        for cell in self.cells:
            if cell['type'] == 'md':
                self.notebook['cells'].append(new_md_cell(cell['source']))
            if cell['type'] == 'py':
                self.notebook['cells'].append(new_py_cell(cell['source']))

        nb.write(self.notebook, self.filename, version=4)
        return self
    
    def add_calibration(self, calibration) -> Report:
        """Appends a calibration to the report.
        
        Args:
            calibration: Instance of the current Calibration class.
        """
        self.last_calibration = len(self.cells)
        for cell in calibration.report_templ:
            src = cell['source'].splitlines()
            
            # Handle conditional cells
            if keep_cell(src):
                if src[0][:3] == '#if':
                    src = src[1:]
                if cell['cell_type'] == 'code':
                    self.add_py_cell('\n'.join(src))
                if cell['cell_type'] == 'markdown':
                    self.add_md_cell('\n'.join(src))
        return self
        
    def add_results(self, calibration) -> Report:
        """Reports results from the current calibration.
        
        """
        self.log.info(calibration.pre, 'Comparing assumptions before and assumptions after')
        self.assump_aftr = json.dumps(self.assumptions, indent=4)
        diff = list(get_diff(
            self.assump_befr.splitlines(keepends=True),
            self.assump_aftr.splitlines(keepends=True)
        ))

        self.log.info(calibration.pre, 'Updating assumptions after and assumptions diff')
        self.cells[self.cell_aftr]['source'] = self.assump_aftr+';'
        self.cells[self.cell_diff]['source'] = ['# Assumptions diff\n\n', '```diff\n', *diff, '```']
        return self.update()

    def add_md_cell(self, src) -> Report:
        self.cells.append({'type': 'md', 'source': src})
        return self.update()

    def add_py_cell(self, src) -> Report:
        self.cells.append({'type': 'py', 'source': src})
        return self.update()

    def ins_md_cell(self, pos: int, src) -> Report:
        self.cells.insert(pos, {'type': 'md', 'source': src})
        return self.update()

    def ins_py_cell(self, pos: int, src) -> Report:
        self.cells.insert(pos, {'type': 'py', 'source': src})
        return self.update()