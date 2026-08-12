#!/usr/bin/env python

import os
import numpy as np
from pathlib import Path

plot_styles = "styles/paperdraft.mplstyle"

lattice_sizes = [24, 28, 32, 36, 40]
beta_slugs = [920, 940, 960, 980, 100, 102, 104, 108, 110, 114, 120, 128, 136, 146]
operators = ["plaq", "sym"]
times = np.arange(2.5, 6.8, 0.1) # does not include 6.8
gsquared = np.arange(1.8, 10.4, 0.1)

interpolate_fit_order = 4

ts = {0.1 : {'tmins' : [3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0],
             'tmaxs' : [5.0, 5.5, 6.0]},
      0.2 : {'tmins' : [2.5, 3.5],
             'tmaxs' : [6.0, 6.8]} }
dts = [0.1, 0.2] 


def task_download_data():
  """
  Download raw data release from zenodo.
  """
  output_dir = 'raw_data'
  doi =  '10.5281/zenodo.10719052'

  output = [os.path.join(output_dir, f"l{NX}t{NX}b{beta}.txt") for NX in lattice_sizes for beta in beta_slugs]

  return {
          'actions': [['uvx', 'zenodo_get', '-d', doi, '-o', output_dir]],
          'targets': output,
          'verbosity': 2
         }

def task_extrapolate_infinite_volume():
  """
  compute infinite volume extrapolation
  """
  working_dir = Path('./raw_data')
  raw_data = list(working_dir.glob('*.txt'))

  filename_template = "l{NX}t{NX}b{beta}.txt"
  script = os.path.join("src", "extrapolate_infinite_volume.py")

  output_dir = os.path.join('intermediary_data', 'infinite_volume')
  os.makedirs(output_dir, exist_ok=True)

  for beta in beta_slugs:
    inputs = [os.path.join('raw_data', f"l{NX}t{NX}b{beta}.txt") for NX in lattice_sizes]
    for time in times:
      for op in operators:
        output = os.path.join(output_dir, f"b{beta}_t{time:.1f}_{op}.json.gz")
        yield {
                'name': f"{op}:b{beta}:t{time:.1f}",
                'actions': [['python', script, *inputs, '--output_filename', output, '--operator', op, '--time', f"{time:.1f}"]],
                'file_dep': inputs,
                'targets': [output],
                'verbosity': 2 
              }

def task_interpolate_finite_a():
  """
  interpolate between beta and coupling at fixed t/a^2
  """

  input_dir = os.path.join('intermediary_data', 'infinite_volume')
  output_dir = os.path.join('intermediary_data', 'beta_interpolation')
  os.makedirs(output_dir, exist_ok=True)
  script = os.path.join('src', 'fit_beta_against_g2.py')
  
  for op in operators:
    for time in times:
      output = os.path.join(output_dir, f"t{time:.1f}_{op}.json.gz")
      inputs = [os.path.join(input_dir, f"b{beta}_t{time:.1f}_{op}.json.gz") for beta in beta_slugs]
      yield {
              'name': f"{op}:t{time:.1f}",
              'actions': [['python', script, *inputs, '--order', str(interpolate_fit_order), '--output_filename', output]],
              'file_dep': inputs,
              'targets': [output],
              'verbosity': 2
            }

def task_extrapolate_continuum():
  """
  do the continuum extrapolation
  """
  input_dir = os.path.join('intermediary_data', 'beta_interpolation')
  output_dir = os.path.join('intermediary_data', 'continuum_extrapolation')
  os.makedirs(output_dir, exist_ok=True)
  script = os.path.join('src', 'extrapolate_continuum.py')
  
  for op in operators:
    for g2 in gsquared:
      for dt in dts:
        for tmin in ts[dt]['tmins']:
          for tmax in ts[dt]['tmaxs']:  
            output = os.path.join(output_dir, f"{op}_gsquared{g2:.1f}_tmin{tmin}_tmax{tmax}_dt{dt}.json.gz")
            inputs = [os.path.join(input_dir, f"t{time:.1f}_{op}.json.gz") for time in np.arange(tmin,tmax+0.01,dt)]
            yield {
                    'name': f"{op}:g{g2:.1f}:tmin{tmin}:tmax{tmax}:dt{dt}",
                    'actions': [['python', script, *inputs, '--g_squared', f"{g2:.1f}", '--output_filename', output]],
                    'file_dep': inputs,
                    'targets': [output],
                    'verbosity': 2
                  }

                 
    
