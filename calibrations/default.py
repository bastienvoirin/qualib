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
            
        splt = [key[1:].split('/') for key in keys] # Strip leading '$' and split at '/'
        
        # Handle placeholders
        for i, key in enumerate(splt):
            val = 'MISSING_ASSUMPTION'
            if key[0] in assumptions.keys():
                # $section/parameter
                if len(key) > 1:
                    if key[1] in assumptions[key[0]].keys():
                        val = str(assumptions[key[0]][key[1]])
                    else:
                        raise Exception(f'Missing assumption "{"/".join(key)}"')
                # $parameter
                else:
                    val = str(assumptions[key[0]])
            else:
                raise Exception('Missing assumption "{}"'.format('/'.join(key)))
            token = '$'+'/'.join(key)
            if token == '$filename':
                val = f'{timestamp}_{calib_id:03d}_{calib_name}{"_"+sub_name if sub_name else ""}.h5'
            print(f'    {token} = {val}')
            template = template.replace(token, val)
            
        with open(f'calibrations/{calib_name}/{calib_name}.meas.ini', 'w') as f:
            f.write(template)
            
        self.keys = keys # List of placeholders
        self.repl = ['$'+'/'.join(key) for key in splt] # List of placeholders after substitutions
        self.result = {}
        self.calib_id = calib_id
        self.calib_name = calib_name
        
    def pre_report(self, calib_name, calib_id, sub_name, sub_repl, timestamp, assumptions, repl):
        """
        """
        #path = f'\'{assumptions["default_path"]}/{timestamp}_{calib_id:03d}_{calib_name}_{sub_name}.h5\''
        path = f'\'../test_meas/{calib_id:03d}_{calib_name}.h5\''
        header = f'{"="*70}\n[{calib_name}{"_"+sub_name if sub_name else ""} calibration output]\n'
        print(header)
        
        for i in DefaultJupyterReport.header:
            if i['type'] == 'code':
                code = '\n'.join(filter(lambda line: line[0] != '%', i['code'].split('\n')))
                exec(code, globals(), locals())
                
        with open(f'calibrations/{calib_name}/template_{calib_name}.ipynb', 'r', encoding='utf-8') as f:
            cells = f.read()
            result = {}
            
            for key, val in repl.items():
                cells = cells.replace(key, val)
            
            # Fetch analysis code from .ipynb template and compute result
            for cell in json.loads(cells)['cells']:
                if cell['cell_type'] == 'code':
                    try:
                        loc = locals()
                        src = ''.join(cell['source'])
                        src = src.replace('§HDF5_PATH§', path)
                        for key, val in sub_repl.items():
                            src = src.replace(f'§{key}§', f'\'{val}\'')
                        exec(src, globals(), loc)
                        result = loc['result']
                        print(result)
                    except:
                        raise
            
            self.result = result
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
        
default_header = [
    {'type': 'text', 'text': '# Report'},
    {'type': 'code', 'code': '''# Default header, defined in qualib/calibrations/default.py
%matplotlib notebook
import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib as mpl
import matplotlib.animation as animation
import matplotlib.colors as colors
from mpl_toolkits.mplot3d import Axes3D 
import matplotlib.cm as cm
import scipy as sc
import scipy.optimize as opt
import scipy.ndimage as sci
import scipy.signal as scs
import time
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import scipy
from qutip.wigner import qfunc, wigner
import qutip'''},
    {'type': 'code', 'code': '''\
def IQ_rot(data):
    dataf = data.flatten()
    I = np.real(dataf)
    Q = np.imag(dataf)
    Cov = np.cov(I,Q)
    A = scipy.linalg.eig(Cov)
    eigvecs = A[1]
    if A[0][1] > A[0][0]:
        eigvec1 = eigvecs[:,0]
    else:
        eigvec1 = eigvecs[:,1]
    theta = np.arctan(eigvec1[0]/eigvec1[1])
    data_c = data * np.exp(1j*theta)
    return data_c'''}
]

class DefaultJupyterReport:
    header = default_header

    def __init__(self):
        self.header = default_header
        self.notebook = nbfv4.new_notebook()
        self.cells = []
    
    def initialize(self, assumptions, calib_scheme_str):
        self.assumptions_before = json.dumps(assumptions, indent=4)
        self.add_md_cell('# Calibration sequence')
        self.add_py_cell(calib_scheme_str.strip()+';')
        self.add_md_cell('# Assumptions before calibration sequence')
        self.add_py_cell(self.assumptions_before+';')
        
        for cell in default_header:
            if cell['type'] == 'code':
                self.add_py_cell(cell['code'])
            elif cell['type'] == 'text':
                self.add_md_cell(cell['text'])
        
    def finish(self, report_filename, assumptions):
        self.assumptions_after = json.dumps(assumptions, indent=4)
        before = self.assumptions_before.splitlines(keepends=True)
        after = self.assumptions_after.splitlines(keepends=True)
        diff = difflib.Differ().compare(before, after)
        diff = [line for line in diff if line[0] in ['+', '-']]
        
        with open(report_filename, 'r') as f:
            report = json.loads(f.read())
            for i, cell in enumerate(report['cells']):
                # Insert assumptions after calibration sequence and assumptions diff
                if cell['cell_type'] == 'markdown' and cell['source'][0] == '# Report':
                    cls = DefaultJupyterReport
                    cls.ins_md_cell(report, i,   ['# Assumptions after calibration sequence'])
                    cls.ins_py_cell(report, i+1, (self.assumptions_after+';').splitlines(keepends=True))
                    cls.ins_md_cell(report, i+2, ['# Assumptions diff\n\n', '```diff\n', *diff, '```'])
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