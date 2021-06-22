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

def get_diff(prev, next):
    """
    Args:
        prev (`list` of `str`):
        next (`list` of `str`):

    Returns:
        `list` of `str`: Difference between ``prev`` and ``next``.
    """
    return [line for line in difflib.Differ().compare(prev, next) if line[0] in ('+', '-')]

def keep_cell(src):
    """Handles conditional cells: skips a given cell if its first line is ``#if condition:`` and ``condition`` evaluates to ``False``.
    
    Args:
        src (`list` of `str`): Lines of a given cell

    Returns:
        bool:
    """
    first_line = src[0].strip()
    return first_line[:3] != '#if' or eval(first_line[4:-1])

######################################################################

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
        log (Log):
        report (Report):
        assumptions (dict):
        id (int):
        name (str):
        substitutions (dict):
        exopy_templ:
        pre (str):
        timestamp (str):
        report_templ:
        hdf5_path (str)
        results (dict):
    """
    
    def __init__(self, log, report, assumptions, id, name, substitutions, exopy_templ, pre, timestamp):
        self.log           = log
        self.report        = report
        self.assumptions   = assumptions
        self.id            = id
        self.name          = name
        self.substitutions = substitutions
        self.exopy_templ   = exopy_templ
        self.pre           = pre
        self.timestamp     = timestamp

        self.report_templ  = nbf.read(f'qualib/calibrations/{name}/template_{name}.ipynb', as_version=4).cells
        self.hdf5_path     = f'{assumptions["default_path"]}/{timestamp}_{id:03d}_{pre[:-1]}.h5'
        self.results       = {}
    
    def handle_substitutions(self):
        """Handles substitutions. Should be called at the end of :py:func:`Calibration.handle_substitutions`.
        
        Returns:
            `None`
        """
        for key, val in self.substitutions.items():
            # Handle substitutions in Exopy template
            self.exopy_templ = self.exopy_templ.replace(key, val)

            # Handle substitutions in report template
            for i in range(len(self.report_templ)):
                self.report_templ[i].source = self.report_templ[i].source.replace(key, val)

    def pre_process(self, mapping = {}):
        """Handles pre-placeholders. Should be called at the end of :py:func:`Calibration.pre_process`.

        Args:
            mapping (dict): Dictionary of ``'PRE_PLACEHOLDER': value`` pairs.
        
        Returns:
            `None`
        """
        # Handle pre-placeholders in Exopy template
        exopy_templ_befr = self.exopy_templ.splitlines()
        pre_placeholders = re.findall(r'(\$([a-z0-9_]+)(?:/([a-z0-9_]+))?)', self.exopy_templ, re.MULTILINE)
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

        meas_path = f'qualib/calibrations/{self.name}/{self.name}.meas.ini'
        self.log.info(self.pre, f'Generating "{meas_path}"')
        with open(meas_path, 'w', encoding='utf-8') as f:
            f.write(self.exopy_templ)

        # Handle pre-placeholders in report template
        mapping['HDF5_PATH'] = self.hdf5_path
        for key, val in mapping.items():
            for i in range(len(self.report_templ)):
                self.report_templ[i]['source'] = self.report_templ[i]['source'].replace(key, val)

    def process(self):
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
                code = '\n'.join(filter(lambda line: line[0] != '%', cell['source'].splitlines())) # Handle magic commands
                try:
                    exec(code, globals(), locals())
                except:
                    self.log.debug('', code.splitlines())
                    raise

        self.log.info(self.pre, f'Executing "qualib/calibrations/{self.name}/template_{self.name}.ipynb" code cells')
        loc = locals()
        for cell in self.report.cells[self.report.last_calibration:]:
            if cell['type'] == 'py':
                try:
                    exec(cell['source'], loc, loc)
                except:
                    self.log.debug('', cell['source'].splitlines())
                    raise
                if '_results' in loc and '_results' in cell['source']:
                    self.log.info(self.pre, 'Fetching results')
                    self.results = loc['_results']

                if '_opt' in loc and '_cov' in loc and '_opt' in cell['source'] and '_cov' in cell['source']:
                    self.log.info(self.pre, 'Checking standard deviations against optimized values')
                    ratios  = np.sqrt(np.diag(loc['_cov'])) / np.abs(loc['_opt'])
                    failed  = ', '.join([f'_opt[{ind}]' for ind in np.where(ratios > 0.05)[0]])
                    message = f'Standard deviation too large for {failed}\n'\
                              f'  If a parameter is not relevant, exclude it '\
                              f'from _opt and _cov in template_{self.name}.ipynb'
                    assert all(ratios <= 0.05), (self.log.error(self.pre, message) and False) or message
                    
                if '_err' in loc and '_err' in cell['source']:
                    self.log.info(self.pre, 'Handling custom errors')
                    errors = []
                    for message, condition in loc['_err'].items():
                        if condition:
                            errors.append(message)
                            self.log.error(self.pre, message)
                    assert not errors, '\n  '+'\n  '.join(errors)

    def post_process(self, mapping):
        """Handles post-placeholders. Should be called at the end of :py:func:`Calibration.post_process`.
        
        Args:
            mapping (dict): Dictionary of ``'POST_PLACEHOLDER': value`` pairs.
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
        filename (str): Report filename.
        assumptions (dict): State of the assumptions before the calibrations.
        calib_scheme_str (str): String representation of the calibration sequence.
            
    Attributes:
        log (Log):
        filename (str):
        header (list): Default header cells.
        notebook:
        cells (list):
        assumptions_befr (str): Assumptions before the current calibration.
        assumptions_aftr (str): Assumptions after the current calibration.
        cell_befr (int): Position of the cell receiving the assumptions before the current calibration.
        cell_aftr (int): Position of the cell receiving the assumptions before the current calibration;
    """
        
    def __init__(self, log, filename, assumptions, calib_scheme_str):
        self.log      = log
        self.filename = filename
        self.header   = nbf.read('qualib/calibrations/default_header.ipynb', as_version=4).cells
        self.notebook = nbfv4.new_notebook()
        self.cells    = []

        self.assumptions_befr = json.dumps(assumptions, indent=4)

        self.add_md_cell('# Calibration sequence')
        self.add_py_cell(calib_scheme_str.strip()+';')
        self.add_md_cell('# Assumptions before calibration sequence')
        self.add_py_cell(self.assumptions_befr+';')

        self.add_md_cell('# Assumptions after calibration sequence')
        self.cell_aftr = len(self.cells)
        self.add_py_cell('')
        self.cell_diff = len(self.cells)
        self.add_md_cell('# Assumptions diff')
        
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
        self.last_calibration = len(self.cells)
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
        
    def add_results(self, calibration, assumptions):
        """Reports results from the previous calibration.
        
        Args:
            assumptions (dict): Dictionary of assumptions.
            
        Returns:
            Report: ``self``.
        """
        self.log.info(calibration.pre, 'Comparing assumptions before and assumptions after')
        self.assumptions_aftr = json.dumps(assumptions, indent=4)
        diff = get_diff(
            self.assumptions_befr.splitlines(keepends=True),
            self.assumptions_aftr.splitlines(keepends=True)
        )

        self.log.info(calibration.pre, 'Updating assumptions after and assumptions diff')
        self.cells[self.cell_aftr]['source'] = self.assumptions_aftr+';'
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