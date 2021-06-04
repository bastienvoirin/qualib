import re
import nbformat as nbf
import nbformat.v4 as nbfv4
import json

class DefaultCalibration:
    """
    Default meas.ini file generator from Exopy template and assumptions file
    A placeholder must have the format '$param' or '$section/param' where
    <section> and <param> are alphanumeric strings ('a'-'z', 'A'-'Z', '0'-'9', '_')
    """
    def __init__(self, template, assumptions, calib_id, calib_name, sub_name, sub_repl):
        keys = re.findall(r'\$[a-zA-Z_/]+', template, re.MULTILINE) # placeholders
        splt = [key[1:].split('/') for key in keys] # strip leading '$' and split at '/'
        
        # handle substitutions
        for i, key in enumerate(splt):
            for j, part in enumerate(key):
                if part in sub_repl:
                    splt[i][j] = sub_repl[part]
        for src, dst in sub_repl.items():
            template = template.replace(src, dst)
        
        # handle placeholders
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
                    val = f'{calib_id:03d}_{calib_name}.h5'
                print(f'    {token} = {val}')
                template = template.replace(token, val)
            
        with open(f'calibrations/{calib_name}/{calib_name}.meas.ini', 'w') as f:
            f.write(template)
            
        self.keys = keys # list of placeholders
        self.repl = ['$'+'/'.join(key) for key in splt] # list of placeholders after substitutions
        self.result = {}
        self.calib_id = calib_id
        self.calib_name = calib_name
        
    def report(self, calib_name, sub_name, sub_repl, report_filename, cells_json):
        report = ''
        with open(report_filename, 'r') as f:
            report = json.loads(f.read())
            report['cells'] += cells_json
            report = json.dumps(report, indent=4)
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
default_header = [
    {'type': 'text', 'text': '# Report'},
    {'type': 'code', 'code': '''\
# Default header, defined in qualib/calibrations/default.py
%matplotlib nbagg
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
from qutip.wigner import qfunc, wigner
import qutip
import scipy'''},
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
    # theta = theta%np.pi # added 19/07/2019
    data_c = data * np.exp(1j *theta)
    return data_c'''}
]

class DefaultJupyterReport:
    def __init__(self):
        self.header = default_header
        self.notebook = nbfv4.new_notebook()
        self.cells = []
    
    def initialize(self, assumptions):
        self.add_md_cell('# Assumptions before calibration sequence')
        self.add_py_cell(json.dumps(assumptions, indent=4))
        for cell in default_header:
            # cell == {'type': 'code', 'code': '____'}
            if cell['type'] == 'code':
                self.add_py_cell(cell['code'])
            # cell == {'type': 'md', 'text': '____'}
            elif cell['type'] == 'text':
                self.add_md_cell(cell['text'])
        
    def finish(self, report_filename, assumptions):
        # insert assumptions after calibration sequence
        src = json.dumps(assumptions, indent=4).split('\n')
        src = [f'{line}\n' if i+1<len(src) else line for i, line in enumerate(src)]
        report = ''
        with open(report_filename, 'r') as f:
            report = json.loads(f.read())
            for i, cell in enumerate(report['cells']):
                if cell['cell_type'] == 'markdown' and cell['source'][0] == '# Report':
                    report['cells'].insert(i, {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": ["# Assumptions after calibration sequence"]
                    })
                    report['cells'].insert(i+1, {
                        "cell_type": "code",
                        "execution_count": None,
                        "metadata": {},
                        "outputs": [],
                        "source": src
                    })
                    break
            report = json.dumps(report, indent=4)
        
        with open(report_filename, 'w') as f:
            f.write(report)
    
    # append Markdown cell
    def add_md_cell(self, text):
        cell = nbfv4.new_markdown_cell(text)
        self.cells.append(cell)
        self.notebook['cells'] = self.cells
        return self
    
    # append Python cell
    def add_py_cell(self, code):
        cell = nbfv4.new_code_cell(code)
        self.cells.append(cell)
        self.notebook['cells'] = self.cells
        return self
    
    # save as {filename}
    def create(self, filename):
        with open(filename, 'w') as f:
            nbf.write(self.notebook, f)