# Cache Study

Cache replacement/prefetching policy study.

This repository contains an implementation of RL-based replacement policy exploration. Reinforcement learning is not data-efficient, so the performance is not good enough. A supervised learning method might be a better option for replacement policy exploration 🤗.

Also, this repository contains a unified cache replacement & prefetch policy implementation.

Note that there might be bugs, errors or improper experiment settings in this repository.

## Source Code Walkthrough

- `replacement/` contains the implementation of RLR replacement policy and a cache trace generator.
- `scripts/` contains some testing and plotting scripts.
- `unified/` contains the implementation of unified cache replacement & prefetch policy.

## About

This repository is for NKU Computer Architecture course study project. IF YOU WANT TO USE SOME PARTS OF THIS REPOSITORY, PLEASE CONTACT ME FIRST AND CITE THIS REPOSITORY.

本仓库是南开大学计算机体系结构课程的探究项目。**如果需要使用/参考本仓库的部分代码，请先联系我并在报告/仓库中注明出处。**
