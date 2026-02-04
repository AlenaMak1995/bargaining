This repository reproduces the counterfactual bargaining algorithm from **Counterfactual Programming for Optimal Control**, validates it on numeric CMDPs, and extends it to logical (PCTL-style) constraints via augmented MDPs.

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

## What Is Reproduced

- Counterfactual bargaining primal–dual loop
- Occupancy-measure LP formulation
- Endogenous slack variables with quadratic penalties
- Support for **multiple constraints** (energy, time, logic)
- Paper-style dual updates using previous-iterate residuals

## What Is Extended

- Unified LP formulation with arbitrary linear constraints
- Extension to **PCTL reachability and Until formulas**
- Augmented MDP construction with region and Until flags

## Repository Structure (In process of editing)

- grid/ # GridWorld and slip-MDP models
- numeric/ # Numeric CMDP bargaining experiments
- pctl/ # PCTL and Until specifications
- lp_solvers.py # Global LP baselines
- bargaining_numeric_constraints.py
- pctl_solvers.py # Augmented MDP + PCTL LP construction
- scripts/ # Reproducibility scripts
- configs/ # Experiment configs

## Mathematical Formulation

### CMDP and Occupancy Measures
We consider a finite Markov Decision Process

![CMDP formulation](theory/cmdp1.png) 

where *S* is a finite state space, *A* a finite action space, *T(s,a,s')* the probability transition matrix, and *s_0* the initial state.
Goal states are absorbing.

Instead of policies, we work with *occupancy measures*

![Occupancy](theory/occupancy.png) 

which represent the expected number of times action *a* is taken in state *s*.

### Flow constraints

Occupancy measures satisfy the SSP flow constraints

![Flow](theory/flow.png) 

which can be written compactly in matrix form as

![Flow matrix](theory/flow_matrix.png) 

### Objective and Resource constraints

Let c ∈ R^{|E|} denote the primary cost vector and f_i ∈ R^{|E|} denote linear resource cost vectors (e.g., energy, time), with corresponding budgets B_i ∈ R.

The hard-constrained CMDP is:

![Hard CMDP](theory/cmdp_formulation.png) 

This problem may be infeasible or overly restrictive.

### Counterfactual Bargaining Relaxation

Following the counterfactual bargaining framework, each hard constraint is relaxed by introducing a nonnegative slack variable *s_i*:

![Slack](theory/slack_penalty.png) 

The counterfactual bargaining framework does not modify the optimization problem directly. Instead, it introduces a *specification cost*
function

![Cost](theory/cost.png)

where *β_i* > 0 controls the cost of violating constraint *i*. 

We also optionally include a strongly convex regularizer (ρ^2 ∥x∥2)/2 with ρ > 0. 

The role of $h$ is not to regularize the objective, but to define a *compromise specification* that trades off performance improvement
against specification cost. Following paper formulation, the compromise specification *s†* is characterized by the condition

∇h(s) = λ*(s)

where λ*(s) denotes the optimal dual variables of optimisation problem for the specification *s*.

Algorithm 1 enforces this equilibrium implicitly by coupling the primal–dual dynamics with the inverse map s = (∇h)^{-1}(λ). For quadratic specification costs
h(s) = Σ_i (1/(2β_i)) s_i², this yields the explicit relation

  s_i = β_i λ_i,

which can be interpreted as an endogenously adjusted specification level that increases only when the corresponding constraint remains difficult to satisfy.

At equilibrium, the resulting saddle point corresponds to the KKT conditions of the following slack-augmented optimization problem:

![Problem](theory/opt_penalty.png)

The primal–dual algorithm in the paper enforces its optimality conditions implicitly via counterfactual updates of the dual variables.

### Algorithms Implemented

#### Numeric Counterfactual Bargaining

**Problem setup**

We consider a stochastic shortest-path gridworld with slip probability 0.1.
The agent starts at **S** and aims to reach **G**, minimizing price while
satisfying energy and time budgets (possibly relaxed via bargaining).

**Cost grids:**

<p align="center">
  <img src="theory/experiments/price.png" width="30%" />
  <img src="theory/experiments/energy.png" width="30%" />
  <img src="theory/experiments/time.png" width="30%" />
</p>

### Experiment overview

| Exp | β_E | β_T | E_max | T_max | Baseline | Bargained Price (raw) | Bargained Penalty |Bargained Total |
|----:|----:|----:|------:|------:|:--------:|------------:|--------:|------:|
| 1 | 1.5 | 1.5 | 3 | 3 | infeasible | 9.88 | 1.25 | 11.13 |
| 2 | 1.5 | 1.5 | 10 | 5 | feasible (6.98) | 6.61 | 0.19 | 6.80 |
| 3 | 10.5 | 1.5 | 10 | 5 | feasible (6.98)  | 4.47 | 1.25 | 5.72 |



#### PCTL / Until Extension

### How to Reproduce Results

#### Numeric Experiments
#### PCTL Experiments

### Expected Outputs

### Notes on Differences from the Paper

### Limitations & Future Work

### Citation
