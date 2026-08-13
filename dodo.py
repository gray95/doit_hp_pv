#!/usr/bin/env python

import os
import numpy as np
from pathlib import Path

plot_styles = "styles/paperdraft.mplstyle"

lattice_sizes = [24, 28, 32, 36, 40]
beta_slugs = [920, 940, 960, 980, 100, 102, 104, 108, 110, 114, 120, 128, 136, 146]
operators = ["plaq", "sym"]
times = np.arange(2.5, 6.8, 0.1) # does not include 6.8
gsquared = np.arange(1.8, 10.5, 0.1)

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

                 
def task_fit_fixed_point():
  """
  Placeholder
  """

  input_dir = os.path.join('intermediary_data', 'continuum_extrapolation')
  output_dir = os.path.join('intermediary_data', 'fixed_point')
  os.makedirs(output_dir, exist_ok=True)
  script = os.path.join('src', 'fit_fixed_point.py')

  fixed_point_g_squareds = np.linspace(4.5, 8.5, 41)
  
  for op in operators:
    for dt in dts:
      for tmin in ts[dt]['tmins']:
        for tmax in ts[dt]['tmaxs']:
          output = os.path.join(output_dir, f"{op}_tmin{tmin}_tmax{tmax}_dt{dt}.json.gz")
          inputs = [os.path.join(input_dir, f"{op}_gsquared{g2:.1f}_tmin{tmin}_tmax{tmax}_dt{dt}.json.gz") for g2 in fixed_point_g_squareds]
          yield {
                  'name': f"{op}:tmin{tmin}:tmax{tmax}:dt{dt}",
                  'actions': [['python', script, *inputs, '--output_filename', output]],
                  'file_dep': inputs,
                  'targets': [output],
                  'verbosity': 2
                }

def task_plot_volume_extrapolation():
  """
  Plot infinite volume extrapolation of flowed coupling and beta for different bare betas and the
  plaquette and symmetric operators.
  """
  input_dir = os.path.join('intermediary_data', 'infinite_volume')
  output_dir = os.path.join('assets', 'plots')
  os.makedirs(output_dir, exist_ok=True)
  script = os.path.join('src', 'plot_infinite_volume_extrapolation.py')

  plot_beta_slugs = [960, 980, 102]
  plot_times = [2.5, 3.5, 4.5, 6.0]

  for op in operators:
    output = os.path.join(output_dir, f"volume_extrapolation_{op}.pdf")
    inputs = [os.path.join(input_dir, f"b{beta}_t{time:.1f}_{op}.json.gz") for beta in plot_beta_slugs for time in plot_times]
    yield {
            'name': f"{op}",
            'actions': [['python', script, *inputs, '--output_filename', output, '--plot_styles', plot_styles]],
            'file_dep': inputs,
            'targets': [output],
            'verbosity': 2
          }

def task_plot_finite_a_interpolation():
  """
  Plot interpolation of beta against squared coupling at various t/a^2.
  """
  input_dir = os.path.join('intermediary_data', 'beta_interpolation')
  output_dir = os.path.join('assets', 'plots')
  os.makedirs(output_dir, exist_ok=True)
  script = os.path.join('src', 'plot_beta_against_g2.py')

  plot_times = [2.5, 3.5, 4.5, 6.0]

  for op in operators:
    output = os.path.join(output_dir, f"beta_interpolation_finite_a_{op}.pdf")
    inputs = [os.path.join(input_dir, f"t{time:.1f}_{op}.json.gz") for time in plot_times]
    yield {
            'name': f"{op}",
            'actions': [['python', script, *inputs, '--plot_filename', output, '--plot_styles', plot_styles]],
            'file_dep': inputs,
            'targets': [output],
            'verbosity': 2
          }

def task_plot_continuum_beta():
  """
  Plot continuum beta function for the SU(3) theory with 12 fundamental flavours.
  """
  input_dir = os.path.join('intermediary_data', 'continuum_extrapolation')
  output_dir = os.path.join('assets', 'plots')
  os.makedirs(output_dir, exist_ok=True)
  script = os.path.join('src', 'plot_beta_against_g2_continuum.py')

  output = os.path.join(output_dir, "continuum_betafunction.pdf")
  inputs = [os.path.join(input_dir, f"{op}_gsquared{g2:.1f}_tmin3.5_tmax6.0_dt0.2.json.gz") for op in operators for g2 in gsquared]
  return {
          'actions': [['python', script, *inputs, '--plot_filename', output, '--plot_styles', plot_styles]],
          'file_dep': inputs,
          'targets': [output],
          'verbosity': 2
        }

def task_plot_continuum_extrapolation():
  """
  Plot continuum extrapolation of beta at fixed coupling.
  """
  input_dir = os.path.join('intermediary_data', 'continuum_extrapolation')
  output_dir = os.path.join('assets', 'plots')
  os.makedirs(output_dir, exist_ok=True)
  script = os.path.join('src', 'plot_continuum_extrapolation.py')

  plot_g_squareds = [2.0, 4.0, 6.0, 8.0]
  plot_tick_times = ['2.0', '2.5', '3.5', '4.5', '6.0']

  output = os.path.join(output_dir, "continuum_extrapolation.pdf")

  fit_data = [os.path.join(input_dir, f"{op}_gsquared{g2:.1f}_tmin3.5_tmax6.0_dt0.2.json.gz") for op in operators for g2 in plot_g_squareds]
  unfit_data = [os.path.join(input_dir, f"{op}_gsquared{g2:.1f}_tmin2.5_tmax6.8_dt0.2.json.gz") for op in operators for g2 in plot_g_squareds]

  return {
          'actions': [['python', script, *fit_data, '--unfit_filenames', *unfit_data, '--tick_times', *plot_tick_times, '--output_file', output, '--plot_styles', plot_styles]],
          'file_dep': fit_data+unfit_data,
          'targets': [output],
          'verbosity': 2
         }

def task_plot_fixed_point_scan():
  """
  Plot RG fixed point and its leading irrelevant critical exponent for different values of tmax.
  """
  input_dir = os.path.join('intermediary_data', 'fixed_point')
  output_dir = os.path.join('assets', 'plots')
  os.makedirs(output_dir, exist_ok=True)
  script = os.path.join('src', 'plot_fixed_point_scan.py')

  output = os.path.join(output_dir, "fixed_point_scan.pdf")
  inputs = [os.path.join(input_dir, f"{op}_tmin{tmin}_tmax{tmax}_dt0.1.json.gz") for op in operators for tmin in ts[0.1]['tmins'] for tmax in ts[0.1]['tmaxs']]

  return {
          'actions': [['python', script, *inputs, '--plot_filename', output, '--plot_styles', plot_styles]],
          'file_dep': inputs,
          'targets': [output],
          'verbosity': 2
        }


