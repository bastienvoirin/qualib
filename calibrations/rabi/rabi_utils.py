from re import sub
import time
import numpy as np
from matplotlib import pyplot as plt
import scipy
import scipy.optimize as opt
import h5py
from ..default import DefaultCalibration, DefaultJupyterReport
from inspect import getsource
import nbformat as nbf
import nbformat.v4 as nbfv4
import json

class Calibration(DefaultCalibration):
    """
    meas.ini file generator from Exopy template and assumptions file
    """
    def show(type, fig, ax, axes, plt_args):
        """
        <type>:
            0: single 2D plot
            1: multiple 2D plots
            2: single 3D plot
        <axes>: list of datasets of equal length
            type == 0: axes == [x, y]
            type == 1: axes == [x, y1, y2, ..., yN]
            type == 2: axes == [x, y, z]
        <fig>:
            matplotlib.pyplot figure
        <ax>:
            matplotlib.pyplot axes
            
        fig, ax = plt.subplots()
        """
        
        if type == 0: # Single 2D plot
            ax.plot(axes[0], axes[1], *plt_args)
            
        elif type == 1: # Multiple 2D plots
            for series in axes[1:]:
                ax.plot(axes[0], series, *plt_args)
                
        elif type == 2: # Single 3D plot
            plot = ax.pcolormesh(axes[0], axes[1], axes[2], shading='nearest', *plt_args)
            fig.colorbar(plot)
            
    def process(self, calib_id, calib_name, sub_name, sub_repl, report_filename, timestamp, assumptions):
        """
        Analyze and report the current calibration
        """
        #path  = f'\'{assumptions["default_path"]}/{timestamp}_{calib_id:03d}_{calib_name}_{sub_name}.h5\''
        path = f'\'../measurements_rabi/{calib_id:03d}_{calib_name}.h5\''
        cells = None
        
        header = f'{"="*70}\n[{calib_name}_{sub_name} calibration]\n'
        print(header)
        
        for i in DefaultJupyterReport.header:
            if i['type'] == 'code':
                code = '\n'.join(filter(lambda line: line[0] != '%', i['code'].split('\n')))
                exec(code, globals(), locals())
                
        with open('template_rabi.ipynb', 'r', encoding='utf-8') as f:
            cells = f.read()
            result = {}
            
            # Fetch analysis code from .ipynb template and compute result
            for cell in json.loads(cells)['cells']:
                if cell['cell_type'] == 'code':
                    try:
                        loc = locals()
                        exec(''.join(cell['source']).replace('§HDF5_PATH§', path), globals(), loc)
                        result = loc['result']
                        print(result)
                    except:
                        raise
                        pass
            
            self.result = result
                    
            def update_assumptions(asmp, rslt):
                asmp['qubit'][sub_repl['PULSE_AMP']] = rslt['a_rabi']
            update_assumptions(assumptions, result)
            
            # Generate calibration report
            cells = cells.replace('§TYPE§', sub_name)
            cells = cells.replace('§HDF5_PATH§', path)
            
            # TODO: move to default.py?
            cells = cells.replace('§PULSE_LENGTH§', str(assumptions['qubit'][sub_repl['PULSE_LENGTH']]))
            cells = cells.replace('§PULSE_AMP§', f'{self.result["a_rabi"]:f}')
            
            cells_json = json.loads(cells)['cells']
        
        self.pre_report(calib_name, sub_name, sub_repl, report_filename, cells_json)
        self.post_report(calib_name, sub_name, sub_repl, report_filename, cells_json)
        
        footer = '='*70
        print(footer)
        return
    
    def live_view(self):
        """
        Generate and update a live view of raw results
        Return a list of plots
        """
        f = h5py.File('{:03d}_{}.h5'.format(self.calib_id, self.calib_name), 'r', swmr=True)
        pa = f['parameters']
        da = f['data']
        print(pa.keys())
        print(da.keys())
            
        amp   = da['amp']
        data1 = da['I1'][()] + 1j * da['Q1'][()]
        data2 = da['I2'][()] + 1j * da['Q2'][()] 
        data  = IQ_rot((data1 - data2))
        
        def cosine(t, a_rabi, b, c):
            t_arr = np.array(t)
            return b*np.cos(2*np.pi*t_arr/a_rabi)+c

        Nstop = -40
        popt, pcov = opt.curve_fit(cosine, amp[:Nstop], np.real(data[:Nstop]), (amp[-1]*2, -12e-3, 0), maxfev = 100000)
                
        fig, ax = plt.subplots(1,1, figsize=(8, 6))
        
        plot0 = Plot(0, fig, ax, (amp, np.real(data)), ['bo-'])
        plot1 = Plot(0, fig, ax, (amp, cosine(amp,*popt)), ['r--'])
        plot2 = Plot(0, fig, ax, (amp[:Nstop],cosine(amp[:Nstop],*popt, ['r-'])))
        plots = (plot0, plot1, plot2)
        
        return plots

class JupyterReport(DefaultJupyterReport):
    pass