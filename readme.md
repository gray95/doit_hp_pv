# doit re-implementation of [hp_pv](https://github.com/edbennett/hp_pv) analysis workflow

This repo is part of a project examining and evaluating different workflow managers by re-factoring an analysis workflow. This repo contains the re-implementation in [`doit`](https://pydoit.org/).

The open source [data](https://zenodo.org/records/10719052) used in this workflow was originally released as part of [this paper](https://arxiv.org/abs/2402.18038) by Peterson and Hasenfratz.
## Requirements
- [pixi](https://pixi.prefix.dev/latest/installation)
- [Git](https://github.com/git-guides/install-git)

`doit`, `pyerrors`, `matplotlib` and the other packages will be installed by `pixi` during setup.

## Setup

Clone this repo and `cd` into it

```
pixi install 
```

## Running

```
pixi run doit 
```

With the default `--concurrency 6` this workflow takes ?? mins to run end-to-end on an AMD Ryzen 5 5600. On a laptop with an Intel i7-8565U it takes ?? mins.

The plots produced by the workflow are placed in `assets/`

### Useful task commands

Manually set the number of parallel processes with
```
pixi run doit -n <N>
```
### Notes


### To-Do
- [ ] implement all steps in `dodo.py` 
- [ ] confirm wflow runs end-to-end.
- [ ] check reproducible over different machines/OSes.
- [ ] speed up wflow, takes a couple hours end-to-end at present.
- [ ] submit wflow as a slurm job to a remote cluster.
