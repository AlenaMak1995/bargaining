This repository reproduces the counterfactual bargaining algorithm from **Counterfactual Programming for Optimal Control**, validates it on numeric CMDPs, and extends it to logical (PCTL-style) constraints via augmented MDPs.

README.md
├─ Overview / Motivation
├─ Reference Paper
├─ What Is Reproduced
├─ Repository Structure
├─ Mathematical Formulation (Short!)
├─ Algorithms Implemented
│   ├─ Numeric Counterfactual Bargaining
│   └─ PCTL / Until Extension
├─ How to Reproduce Results
│   ├─ Numeric Experiments
│   └─ PCTL Experiments
├─ Expected Outputs
├─ Notes on Differences from the Paper
├─ Limitations & Future Work
└─ Citation

## Overview / Motivation

This repository is a reproducibility and extension study of the *Counterfactual Programming for Optimal Control* algorithm.

The original paper proposes a primal–dual bargaining mechanism that relaxes hard resource constraints by introducing endogenous slack variables, allowing agents to trade constraint violations against
objective value.

In this project, we:
1. Reproduce the original algorithm on numeric CMDPs.
2. Validate convergence behavior and constraint satisfaction.
3. Extend the approach to probabilistic temporal logic (PCTL) constraints using augmented MDPs and occupancy-measure LP formulations.

## Reference

This work is based on:

> **Counterfactual Programming for Optimal Control**  
>Luiz F. O. Chamon, Santiago Paternain, Alejandro Ribeiro, 2nd Annual Conference on Learning for Dynamics and Control / Proceedings of Machine Learning Research 120:1–10, 2020. 

All algorithmic choices marked as “paper-style” follow the original formulation unless stated otherwise.

