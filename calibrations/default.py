import re
import nbformat as nbf
import nbformat.v4 as nbfv4

class DefaultCalibration:
    """
    Default meas.ini file generator from Exopy template and assumptions file
    A placeholder must have the format '$param' or '$section/param' where
    <section> and <param> are alphanumeric strings ('a'-'z', 'A'-'Z', '0'-'9', '_')
    """
    def __init__(self, template, assumptions, calib_id, calib_name, substitutions):
        keys = re.findall(r'\$[a-zA-Z_/]+', template, re.MULTILINE) # placeholders
        splt = [key[1:].split('/') for key in keys] # strip leading '$' and split at '/'
        
        # handle substitutions
        for i, key in enumerate(splt):
            for j, part in enumerate(key):
                if part in substitutions:
                    splt[i][j] = substitutions[part]
        for src, dst in substitutions.items():
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
        
default_header = '''# Default header, defined in qualib/calibrations/default.py
print('a')
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
import analysis_functions as af
import time
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from qutip.wigner import qfunc, wigner
import qutip
import scipy
print('z')'''

class DefaultJupyterReport:
    def __init__(self):
        self.header = default_header
        self.notebook = nbfv4.new_notebook()
        self.cells = []
        self.add_py_cell(self.header)
    
    def add_md_cell(self, text):
        cell = nbfv4.new_markdown_cell(text)
        self.cells.append(cell)
        self.notebook['cells'] = self.cells
        return self
    
    def add_py_cell(self, code):
        cell = nbfv4.new_code_cell(code)
        self.cells.append(cell)
        self.notebook['cells'] = self.cells
        return self

    def generate(self, filename):
        with open(filename, 'w') as f:
            nbf.write(self.notebook, f)