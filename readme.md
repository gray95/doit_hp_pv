# doit re-implementation of [hp_pv](https://github.com/edbennett/hp_pv) analysis workflow

This repo is part of a project examining and evaluating different workflow managers by re-factoring an analysis workflow. This repo contains the re-implementation in [`doit`](https://pydoit.org/).

The open source [data](https://zenodo.org/records/10719052) used in this workflow was originally released as part of [this paper](https://arxiv.org/abs/2402.18038) by Peterson and Hasenfratz.
## Requirements
- [pixi](https://pixi.prefix.dev/latest/installation)
- [Git](https://github.com/git-guides/install-git)
- [LaTeX] for the plots

`doit`, `pyerrors`, `matplotlib` and the other packages will be installed when you first execute `pixi run`.

## Setup

Clone this repo and `cd` into it
```
git clone https://github.com/gray95/doit_hp_pv.git && cd doit_hp_pv
```

## Running

```
pixi run doit -n <N>
```

With `N=6` this workflow takes ~34 mins to run end-to-end on an AMD Ryzen 5 5600. On a laptop with an Intel i7-8565U it takes ?? mins.

The plots produced by the workflow are placed in `assets/`

### Useful commands

```
pixi run doit list
```
### Notes


### To-Do
- [x] implement all steps in `dodo.py` 
- [x] confirm wflow runs end-to-end.
- [ ] check reproducible over different machines/OSes.
- [ ] speed up wflow, takes a couple hours end-to-end at present.
- [ ] submit wflow as a slurm job to a remote cluster.
