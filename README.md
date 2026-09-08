# ARC-AGI-3 Agent Framework

## Project Overview
The ARC-AGI-3 Agent Framework is a robust research platform designed for the Abstract Reasoning Challenge. It provides an autonomous agent architecture (Pholem) that facilitates the development, evaluation, and submission of AI agents capable of solving complex grid-based reasoning tasks. The system includes modular agent definitions, a simulated environment wrapper, and automated evaluation pipelines.

## Getting Started
To begin working with the framework, install the necessary dependencies:
```bash
pip install -r requirements.txt
```
To run a baseline agent against the evaluation environment, use the following command:
```bash
python run_agent.py --agent-type baseline
```

## Evaluation and Submission
The framework supports batch evaluation and automated submission generation for Kaggle:
1. Run batch evaluations: `python batch_evaluator.py`
2. Generate submission files: `python kaggle_submission.py`
The generated files are stored in the `/submissions` directory, formatted according to the competition specifications.