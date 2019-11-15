import argparse
import sys
import os
import pickle

import pykalman as pk
from numpy import ma
from data import load_openl3_time_series as load_data


DEFAULT_SENSOR = '/beegfs/work/sonyc/features/openl3/2017/sonycnode-b827ebefb215.sonyc_features_openl3.h5'

def process_arguments(args):
    parser = argparse.ArgumentParser()

    parser.add_argument('--sensor',
                        dest='sensor', type=str, default=DEFAULT_SENSOR,
                        help='Location of sensor .h5 file containing l3 embeddings')
    
    parser.add_argument('--latent_dim',
                        dest='latent_dim', type=int, default=2,
                        help='Dimensionality of the latent space')
    
    parser.add_argument('--n_iter',
                        dest='n_iter', type=int, default=5,
                        help='Number of iterations in EM training')
    
    parser.add_argument('--data_range',
                        dest='data_range', type=int, default=None,
                        help='Upper index bound on data')
    
    parser.add_argument('--model_name', type=str, default = None,
                        help='Name to store model under')
    
    parser.add_argument('--output_path', type=str,
                        help='Path to store trained pykalman output')
    
    parser.add_argument('--mask_path', type=str, default = None,
                        help='Path to load the mask for the data')
    
    return parser.parse_args(args)

if __name__=='__main__':
    params = process_arguments(sys.argv[1:])
    
    #loads sensor name
    sensor_name = params.sensor.split('/')[-1]
    
    print('Loading data from {}'.format(sensor_name))
    
    #loads data and mask from sensor
    data, mask = load_data(params.sensor)

    #loads additional mask, if present
    if params.mask_path is not None:
        mask_npz = np.load(params.mask_path)
        mask = mask_npz['mask']
    
    #applies mask to data
    data[mask] = ma.masked
    
    #limits data, for testing purposes
    if params.data_range is not None:
        data = data[:params.data_range] 
    
    
    print('Training Kalman Filter: Sensor: {},\t N_Iterations: {},\t Latent Space Dim{}'\
          .format(sensor_name, params.n_iter, params.latent_dim))
    
    #constructs kalman filter to specifications (PCA NOT YET APPIED)
    kf = pk.KalmanFilter(n_dim_state=params.latent_dim,\
                         n_dim_obs=data.shape[1],\
                         em_vars='all')
    
    #runs EM and stores result
    kf_trained = kf.em(data, n_iter=params.n_iter)
    
    print('Training complete, saving result to {}'.format(params.output_path))
    
    #dumps result to pickle file
    if params.model_name is not None:
        model_name = params.model_name+'.pkl'
    else:
        model_name = sensor_name + '_model.pkl'
    
    with open(os.path.join(params.output_path, model_name), 'wb') as fd:
        pickle.dump(kf_trained, fd)

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        