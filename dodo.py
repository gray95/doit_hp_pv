#!/usr/bin/env python

import os
import numpy as np
from pathlib import Path

plot_styles = "styles/paperdraft.mplstyle"

lattice_sizes = [24, 28, 32, 36, 40]
beta_slugs = [920, 940, 960, 980, 100, 102, 104, 108, 110, 114, 120, 128, 136, 146]
operators = ["plaq", "sym"]
times = np.arange(2.5, 6.7, 0.1)

interpolate_fit_order = 4

def task_download_data():
  """
  Download raw data release from zenodo.
  """
  output_dir = 'raw_data'
  doi =  '10.5281/zenodo.10719052'

  data_dir = Path(output_dir)
  raw_data = list(data_dir.glob('*.txt'))

  return {
          'actions': [['uvx', 'zenodo_get', '-d', doi, '-o', output_dir]],
          'targets': raw_data,
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
                'file_dep': raw_data,
                'targets': [output],
                'verbosity': 2 
              }

