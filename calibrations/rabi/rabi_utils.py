import numpy as np
from matplotlib import pyplot as plt
import scipy
import scipy.optimize as opt
import h5py
from ..DefaultCalibration import DefaultCalibration

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
    return data_c

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
        
        if type == 0: # single 2D plot
            ax.plot(axes[0], axes[1], *plt_args)
            
        elif type == 1: # multiple 2D plots
            for series in axes[1:]:
                ax.plot(axes[0], series, *plt_args)
                
        elif type == 2: # single 3D plot
            plot = ax.pcolormesh(axes[0], axes[1], axes[2], shading='nearest', *plt_args)
            fig.colorbar(plot)
                
    def analyze(self, path):
        """
        Analyze the calibration results
        """
        f = h5py.File(path, 'r', swmr=True)
        pa = f['parameters']
        da = f['data']
        print(pa.keys())
        print(da.keys())
        
        amp   = da['amp']
        data1 = da['I1'][()] + 1j * da['Q1'][()]
        data2 = da['I2'][()] + 1j * da['Q2'][()] 
        data  = IQ_rot((data1 - data2))
        
        def cosine(t, t_rabi, b, c):
            t_arr = np.array(t)
            return b*np.cos(2*np.pi*t_arr/t_rabi)+c

        Nstop = -40
        popt, pcov = opt.curve_fit(cosine, amp[:Nstop], np.real(data[:Nstop]), (amp[-1]*2, -12e-3, 0), maxfev = 100000)
        
        result = {'t_rabi': popt[0]}
        units = {'t_rabi': ''}
        self.result = result
        self.units = units
        
    def report(self):
        header = f'{"="*70}\nRabi calibration'
        footer = '='*70
        lines = "\n".join([f'{key} = {val} {self.units[k]}' for key, val in self.result.items()])
        return f'{header}\n{lines}\n{footer}'
    
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
        
        def cosine(t, t_rabi, b, c):
            t_arr = np.array(t)
            return b*np.cos(2*np.pi*t_arr/t_rabi)+c

        Nstop = -40
        popt, pcov = opt.curve_fit(cosine, amp[:Nstop], np.real(data[:Nstop]), (amp[-1]*2, -12e-3, 0), maxfev = 100000)
                
        fig, ax = plt.subplots(1,1, figsize=(8, 6))
        
        plot0 = Plot(0, fig, ax, (amp, np.real(data)), ['bo-'])
        plot1 = Plot(0, fig, ax, (amp, cosine(amp,*popt)), ['r--'])
        plot2 = Plot(0, fig, ax, (amp[:Nstop],cosine(amp[:Nstop],*popt, ['r-'])))
        plots = (plot0, plot1, plot2)
        
        return plots
