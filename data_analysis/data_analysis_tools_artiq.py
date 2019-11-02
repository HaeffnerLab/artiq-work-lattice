import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import stats
from datetime import datetime
import os
import h5py

class data_analysis_artiq():
    
    def __init__(self, experiment_name, start_date, start_time, end_date, end_time, data_path):
        self.experiment_name = experiment_name        
        self.scan_list = {}
        dir_list = [d for d in os.listdir(data_path) if d >= start_date and d <= end_date]
        for d in dir_list:
            experiment_path = os.path.join(data_path, d, experiment_name)
            for f in os.listdir(experiment_path):
                if not (d == start_date and f < start_time) and not (d == end_date and f > end_time):
                    scan_datetime = datetime.strptime(d + ',' + f, '%Y-%m-%d,%H%M_%S.h5')
                    self.scan_list[scan_datetime] = os.path.join(experiment_path, f)
    
    def get_scan_list(self):
        return self.scan_list
        
    def plot_2d_map(self):
        scan_paths = list(self.scan_list.values())
        f0, p = self.get_data(scan_paths[0])
        t = self.calc_dt()
        F,T = np.meshgrid(f0, t)
        P = np.zeros_like(F, dtype=float)

        for i, scan_path in enumerate(scan_paths):
            try:
                f, P[i,:] = self.get_data(scan_path)
            except Exception as e:
                print("skipping scan", scan_path, "due to exception:", e)
                              
        plt.figure(figsize=(8,8))
        plt.pcolor(F,T,P)
        plt.clim(0,1)
        plt.colorbar()
        plt.title("Frequency shift [kHz]")
        plt.xlabel("Frequency [kHz]")
        plt.ylabel("Time [min]")
        plt.show()
    
    def plot_stability(self, plot_linear_fit=False, plot_average=False):
        t = self.calc_dt()
        f = np.zeros_like(t)
        
        scan_paths = list(self.scan_list.values())
        for i, scan_path in enumerate(scan_paths):
            f[i] = self.fit_scan_to_gaussian(scan_path)
            
        plt.figure(1)
        plt.plot(t, f, 'ro', label=self.experiment_name)
        
        if plot_average:
            plt.plot(t,np.ones_like(t)*np.average(f),'r--')
        
        if plot_linear_fit:
            slope, intercept, r_value, p_value, std_err = stats.linregress(t,f)
            line = slope*t + intercept
            print("std_err for linear fit:", std_err)
            plt.plot(t,line,'r--', label='linear fit, slope='+str(slope))

        plt.xlabel('Time [min]')
        plt.ylabel('Frequency shift [kHz]')
        plt.legend(loc='best')

        print("average frequency:", np.average(f), "kHz")
        print("standard deviation:", np.std(f), "kHz")

        return t,f       
    
    def get_data(self, path):
        data_file = h5py.File(path, 'r')
        
        f = []
        p = []        
        for name, scan_data_obj in list(data_file['scan_data'].items()):
            if 'x-axis' in scan_data_obj.attrs.keys():
                f = scan_data_obj[:]
            else:
                p = scan_data_obj[:]
                
        return f, p
    
    def calc_dt(self):
        t = np.zeros(len(self.scan_list))
        
        scan_list_keys = list(self.scan_list.keys())
        first_scan_datetime = scan_list_keys[0]
        for i, scan_datetime in enumerate(scan_list_keys):
            t[i] = (scan_datetime - first_scan_datetime).total_seconds() / 60
        
        return t
                    
    def fit_scan_to_gaussian(self, scan_path, plot_fig=False):        
        f, p = self.get_data(scan_path)
        max_index = np.where(p == p.max())[0][0]
        fmax = f[max_index]
        
        guess = np.array([fmax, p.max(), 3])
        
        model = lambda x, c0, a, w: a * np.exp(-( x - c0 )**2. / w**2.)
    
        # fitting to Gaussian to find the center
        popt, copt = curve_fit(model, f, p, p0=guess)
        center = popt[0]
        
        if plot_fig:        
            plt.figure()            
            plt.plot(f,p,'ro')
            f_th=np.linspace(f.min(),f.max(),100)
            plt.plot(f_th,model(f_th,popt[0],popt[1],popt[2]),'b')
            plt.xlabel("Frequency [kHz]")
            plt.ylabel("Probability")
            plt.show()
        return center
