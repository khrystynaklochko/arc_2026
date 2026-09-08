# ARC-AGI-3: Abstract Reasoning Challenge Environment

## Overview
ARC-AGI-3 is a specialized development environment designed to facilitate the creation, testing, and evaluation of autonomous agents for the Abstract Reasoning Challenge (ARC). This repository provides a robust toolkit for interacting with ARC-like environments, supporting both local simulation and standardized benchmarking.

## Key Features
- **Agent Framework**: A modular base class for building custom reasoning agents.
- **Toolkit Integration**: A comprehensive `ARCToolkit` for managing game states, rendering, and action submission.
- **Batch Evaluation**: Automated evaluation infrastructure to track agent performance across various challenge environments.
- **Kaggle Compatibility**: Built-in support for generating and validating submissions compatible with Kaggle-style evaluation formats.

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Configure your environment variables in `.env`.
3. Run a baseline agent: `python run_agent.py`

## Repository Structure
- `agents/`: Contains agent logic and definitions.
- `environment_files/`: Houses JSON/Python definitions for ARC challenges.
- `evaluations/`: Stores logs and metrics from batch test runs.
- `toolkit.py`: Core utility library for environment interaction.

## Development
This project follows a strict modular design. New agents should inherit from `BaseAgent` in `agents/base_agent.py`. Evaluators can be triggered using `batch_evaluator.py`.
