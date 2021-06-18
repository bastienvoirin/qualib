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
    """Handles conditional cells: skips a given cell if its first line is `#if condition:` and `condition` evaluates to False
    """
    first_line = src[0].strip()
    if first_line[:3] != '#if' or eval(first_line[4:-1]):
        return src[1:]
    return []

class DefaultCalibration:
    """
    Default meas.ini file generator from Exopy template and assumptions file
    A placeholder must have the format '$param' or '$section/param' where
    <section> and <param> are alphanumeric strings ('a'-'z', 'A'-'Z', '0'-'9', '_')
    """
    def old___init__(self, log, template, assumptions, calib_id, calib_name, subs_name, subs_misc, timestamp):
        self.log         = log
        self.template    = template
        self.assumptions = assumptions
        self.id          = calib_id
        self.name        = calib_name
        self.subs_name   = subs_name
        self.subs_misc   = subs_misc
        self.timestamp   = timestamp

        self.pre = ''.join([calib_name, '_'+subs_name if subs_name else '', ':'])

        keys = re.findall(r'\$[a-zA-Z0-9_/]+', template, re.MULTILINE) # Placeholders in Exopy template
        
        # Handle substitutions
        self.log.info(f'{self.pre} Handling "qualib/calibrations/{calib_name}/{calib_name}_template.meas.ini" substitutions')
        for i, key in enumerate(keys):
            for src, dst in subs_misc.items():
                keys[i] = keys[i].replace(src, dst)
        for src, dst in subs_misc.items():
            template = template.replace(src, dst)
            
        # Handle placeholders
        self.log.info(f'{self.pre} Handling "qualib/calibrations/{calib_name}/{calib_name}_template.meas.ini" placeholders')
        for key in keys:
            splt = key[1:].split('/') # Strip leading '$' and split at '/'
            val = 'MISSING_ASSUMPTION'
            assert splt[0] in assumptions.keys(), f'Missing assumption "{key[1:]}"'
            if len(splt) > 1: # $section/parameter
                assert splt[1] in assumptions[splt[0]].keys(), f'Missing assumption "{key[1:]}"'
                val = str(assumptions[splt[0]][splt[1]])
            else: # $parameter
                val = str(assumptions[splt[0]])
            if key == '$filename':
                val = f'{timestamp}_{calib_id:03d}_{calib_name}{"_"+subs_name if subs_name else ""}.h5'
            template = template.replace(key, val)
            
        meas_path = f'qualib/calibrations/{calib_name}/{calib_name}.meas.ini'
        self.log.info(f'{self.pre} Generating "{meas_path}"')
        with open(meas_path, 'w') as f:
            f.write(template)
            
        self.keys = keys
        self.results = {}
        
    def old_pre_process(self, calib_name, calib_id, subs_name, subs_misc, timestamp, assumptions, repl):
        path = f'\'{assumptions["default_path"]}/{timestamp}_{calib_id:03d}_{calib_name}{"_"+subs_name if subs_name else ""}.h5\''
        #path = f'\'../test_meas/{calib_id:03d}_{calib_name}.h5\''
        header = f'{"="*70}\n[{calib_name}{"_"+subs_name if subs_name else ""} calibration output]\n'
        
        self.log.info(f'{self.pre} Executing "qualib/calibrations/default_header.ipynb" code cells')
        for c in Report.header:
            if c['cell_type'] == 'code':
                code = '\n'.join(filter(lambda line: line[0] != '%', c['source'])) # Handle magic commands
                exec(code, globals(), locals())
                
        self.log.info(f'{self.pre} Reading "qualib/calibrations/{calib_name}/template_{calib_name}.ipynb"')
        with open(f'qualib/calibrations/{calib_name}/template_{calib_name}.ipynb', 'r', encoding='utf-8') as f:
            cells = f.read()
            self.log.info(f'{self.pre} Handling pre_process placeholders defined in "qualib/calibrations/{calib_name}/{calib_name}_utils.py"')
            self.log.info(self.log.json(repl))
            for key, val in repl.items():
                cells = cells.replace(key, val)
            
            self.log.info(f'{self.pre} Executing "qualib/calibrations/{calib_name}/template_{calib_name}.ipynb" code cells')
            loc = locals()
            for cell in json.loads(cells)['cells']:
                if cell['cell_type'] == 'code':
                    src = ''.join(cell['source']).replace('HDF5_PATH', path)
                    for key, val in subs_misc.items():
                        src = src.replace(f'§{key}§', f'\'{val}\'')
                        
                    # Handle conditional cells
                    if keep_cell(src.splitlines()):
                        exec(src, loc, loc)
                        
                        if '_results' in loc and '_results' in src:
                            self.log.info(f'{self.pre} Fetching results')
                            self.results = loc['_results']
                            print(self.results)
                            
                        # sigma(value)/value <= 5%
                        if '_opt' in loc and '_cov' in loc and '_opt' in src and '_cov' in src:
                            self.log.info(f'{self.pre} Checking standard deviations against optimized values')
                            ratios  = np.sqrt(np.diag(loc['_cov'])) / np.abs(loc['_opt'])
                            failed  = ', '.join([f'_opt[{ind}]' for ind in np.where(ratios > 0.05)[0]])
                            message = f'\n  Standard deviation too large for {failed}\n'\
                                      f'  If a parameter is not relevant, exclude it '\
                                      f'from _opt and _cov in template_{calib_name}.ipynb'
                            if not all(ratios <= 0.05):
                                self.log.error(f'{self.pre}{message}')
                            assert all(ratios <= 0.05), message
                            
                        if '_err' in loc and '_err' in src:
                            self.log.info(f'{self.pre} Handling custom errors')
                            errors = []
                            for message, condition in loc['_err'].items():
                                if condition:
                                    errors.append(message)
                                    self.log.error(f'{self.pre} {message}')
                            assert not errors, '\n  '+'\n  '.join(errors)
            
            footer = '='*70
            print(footer)
            
            # Filter conditional cells '#if condition:'
            self.log.info(f'{self.pre} Filtering conditional cells')
            def trim(cell):
                if cell['source'][0][:3] == '#if':
                    cell['source'] = cell['source'][1:]
                return cell
            cells = json.loads(cells.replace('HDF5_PATH', f'\'{path[1:-1]}\''))
            cells['cells'] = [trim(cell) for cell in cells['cells'] if keep_cell(cell['source'])]
            return json.dumps(cells, indent=4, ensure_ascii=False)
    
    def old_post_process(self, calib_name, report_filename, cells, repl):
        self.log.info(f'{self.pre} Handling post_process placeholders defined in "qualib/calibrations/{calib_name}/{calib_name}_utils.py"')
        self.log.info(self.log.json(repl))
        for key, val in repl.items():
            cells = cells.replace(key, val)
            
        self.log.info(f'{self.pre} Appending cells to global .ipynb report')
        with open(report_filename, 'r') as f:
            report = json.loads(f.read())
            report['cells'] += json.loads(cells)['cells']
            report = json.dumps(report, indent=4)
            with open(report_filename, 'w') as g:
                g.write(report)


    def __init__(self, log, report, calib_id, calib_name, subs_name, subs_misc):
        """Handles substitutions

        :param Log log:
        :param Report report:
        :param int calib_id:
        :param str calib_name:
        :param str subs_name:
        :param dict subs_misc:
        :return: None
        """
        return

    def pre_process(self, log, report):
        """Handles pre-placeholders

        :param Log log:
        :param Report report:
        :return: None
        """
        return

    def post_process(self, log, report, calib_name, mapping):
        """Handles post-placeholders

        :param Log log:
        :param Report report:
        :param str calib_name:
        :param dict mapping: Dictionary of `'POST_PLACEHOLDER': value` pairs
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
    header = ''
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open('qualib/calibrations/default_header.ipynb') as f:
        header = json.loads(f.read())['cells']

    def __init__(self, filename, assumptions, calib_scheme_str):
        """
        
        :param str filename: Report filename
        :param dict assumptions: State of the assumptions before the calibrations
        :param str calib_scheme_str: String representation of the calibration sequence
        :return: self
        """
        self.header   = Report.header
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
        """Overwrites `self.notebook` from the list of cells `self.cells`

        :return: self
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
        
    def add_results(self, assumptions):
        """Reports results from the previous calibration
        
        :return: self
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
        """Appends a Markdown cell

        :param str source: Raw content of the Markdown cell
        :return: self
        """
        self.cells.append({'type': 'md', 'source': src})
        return self.update()

    def add_py_cell(self, src):
        """Appends a Python cell
        
        :param str source: Raw content of the Python cell
        :return: self
        """
        self.cells.append({'type': 'py', 'source': src})
        return self.update()

    def ins_md_cell(self, pos, src):
        """Inserts a Markdown cell
        
        :param int pos: Position of the new Markdown cell
        :param str src: Source code of the new Markdown cell
        :return: self
        """
        self.cells.insert(pos, {
            'cell_type': 'markdown',
            'metadata':  {},
            'source':    src
        })
        return self.update()

    def ins_py_cell(self, pos, src):
        """Inserts a Python cell
        
        :param int pos: Position of the new Python cell
        :param str src: Source code of the new Python cell
        :return: self
        """
        self.cells.insert(pos, {
            'cell_type':       'code',
            'execution_count': None,
            'metadata':        {},
            'outputs':         [],
            'source':          src
        })
        return self.update()