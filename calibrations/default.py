import re
import nbformat as nbf
import nbformat.v4 as nbfv4
import json
import numpy as np
import scipy
import difflib

class DefaultCalibration:
    """
    Default meas.ini file generator from Exopy template and assumptions file
    A placeholder must have the format '$param' or '$section/param' where
    <section> and <param> are alphanumeric strings ('a'-'z', 'A'-'Z', '0'-'9', '_')
    """
    def __init__(self, template, assumptions, calib_id, calib_name, sub_name, sub_repl, timestamp):
        keys = re.findall(r'\$[a-zA-Z0-9_/]+', template, re.MULTILINE) # Placeholders
        
        # Handle substitutions
        for i, key in enumerate(keys):
            for src, dst in sub_repl.items():
                keys[i] = keys[i].replace(src, dst)
        for src, dst in sub_repl.items():
            template = template.replace(src, dst)
            
        # Handle placeholders
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
                val = f'{timestamp}_{calib_id:03d}_{calib_name}{"_"+sub_name if sub_name else ""}.h5'
            print(f'    {key} = {val}')
            template = template.replace(key, val)
            
        with open(f'calibrations/{calib_name}/{calib_name}.meas.ini', 'w') as f:
            f.write(template)
            
        self.keys = keys
        self.result = {}
        self.calib_id = calib_id
        self.calib_name = calib_name
        
    def pre_report(self, calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions, repl):
        #path = f'\'{assumptions["default_path"]}/{timestamp}_{calib_id:03d}_{calib_name}_{sub_name}.h5\''
        path = f'\'../test_meas/{calib_id:03d}_{calib_name}.h5\''
        header = f'{"="*70}\n[{calib_name}{"_"+sub_name if sub_name else ""} calibration output]\n'
        print(header)
        
        for c in DefaultJupyterReport.header:
            if c['cell_type'] == 'code':
                code = '\n'.join(filter(lambda line: line[0] != '%', c['source'])) # Handle magic commands
                exec(code, globals(), locals())
                
        with open(f'calibrations/{calib_name}/template_{calib_name}.ipynb', 'r', encoding='utf-8') as f:
            cells = f.read()
            for key, val in repl.items():
                cells = cells.replace(key, val)
            
            # Fetch analysis code from .ipynb template and compute result
            for cell in json.loads(cells)['cells']:
                if cell['cell_type'] == 'code':
                    loc = locals()
                    src = ''.join(cell['source'])
                    src = src.replace('§HDF5_PATH§', path)
                    for key, val in sub_repl.items():
                        src = src.replace(f'§{key}§', f'\'{val}\'')
                    exec(src, globals(), loc)
                    if 'result' in loc:
                        self.result = loc['result']
                        print(self.result)
            
            cells = cells.replace('§HDF5_PATH§', path)
            footer = '='*70
            print(footer)
            return cells
    
    def post_report(self, report_filename, cells, repl):
        for key, val in repl.items():
            cells = cells.replace(key, val)
        with open(report_filename, 'r') as f:
            report = json.loads(f.read())
            report['cells'] += json.loads(cells)['cells']
            report = json.dumps(report, indent=4)
            with open(report_filename, 'w') as g:
                g.write(report)

######################################################################

class DefaultJupyterReport:
    header = ''
    with open('calibrations/default_header.ipynb') as f:
        header = json.loads(f.read())['cells']

    def __init__(self):
        self.header = DefaultJupyterReport.header
        self.notebook = nbfv4.new_notebook()
        self.cells = []
    
    def initialize(self, assumptions, calib_scheme_str):
        self.assumptions_before = json.dumps(assumptions, indent=4)
        self.add_md_cell('# Calibration sequence')
        self.add_py_cell(calib_scheme_str.strip()+';')
        self.add_md_cell('# Assumptions before calibration sequence')
        self.add_py_cell(self.assumptions_before+';')
        
        for cell in self.header:
            if cell['cell_type'] == 'code':
                self.add_py_cell(''.join(cell['source']))
            elif cell['cell_type'] == 'markdown':
                self.add_md_cell(''.join(cell['source']))
        
    def finish(self, report_filename, assumptions):
        self.assumptions_after = json.dumps(assumptions, indent=4)
        before = self.assumptions_before.splitlines(keepends=True)
        after = self.assumptions_after.splitlines(keepends=True)
        diff = difflib.Differ().compare(before, after)
        diff = [line for line in diff if line[0] in ['+', '-']]
        
        with open(report_filename, 'r') as f:
            report = json.loads(f.read())
            for i, cell in enumerate(report['cells']):
                if cell['cell_type'] == 'markdown' and cell['source'][0] == '# Assumptions before calibration sequence':
                    cls = DefaultJupyterReport
                    cls.ins_md_cell(report, i+2, ['# Assumptions after calibration sequence'])
                    cls.ins_py_cell(report, i+3, (self.assumptions_after+';').splitlines(keepends=True))
                    cls.ins_md_cell(report, i+4, ['# Assumptions diff\n\n', '```diff\n', *diff, '```'])
                    break
            with open(report_filename, 'w') as g:
                g.write(json.dumps(report, indent=4))
    
    # Append Markdown cell
    def add_md_cell(self, text):
        cell = nbfv4.new_markdown_cell(text)
        self.cells.append(cell)
        self.notebook['cells'] = self.cells
        return self
    
    # Append Python cell
    def add_py_cell(self, code):
        cell = nbfv4.new_code_cell(code)
        self.cells.append(cell)
        self.notebook['cells'] = self.cells
        return self
    
    # Insert Markdown cell
    @classmethod
    def ins_md_cell(cls, notebook, pos, src):
        notebook['cells'].insert(pos, {
            'cell_type': 'markdown',
            'metadata':  {},
            'source':    src
        })
    
    # Insert Python cell
    @classmethod
    def ins_py_cell(cls, notebook, pos, src):
        notebook['cells'].insert(pos, {
            'cell_type':       'code',
            'execution_count': None,
            'metadata':        {},
            'outputs':         [],
            'source':          src
        })
    
    # Save as {filename}
    def create(self, filename):
        with open(filename, 'w') as f:
            nbf.write(self.notebook, f)