# python-project-by-mmcli

This repository showcases Python projects built by Minovative Mind CLI agent.

## Projects

- **Symbolic Calculus Engine**: Located in `all-projects/calculus/` with entry point `main.py` at repository root.

## Getting Started

### Requirements
- **Python 3.8+** (Note: macOS and Linux systems use `python3` rather than `python`).

### Virtual Environment Setup

1. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   ```

2. **Activate Virtual Environment**
   - **macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows (Command Prompt / PowerShell)**:
     ```cmd
     venv\Scripts\activate
     ```

3. **Install Dependencies (if any)**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

### Execution Guide

#### 1. Running via Root `main.py`
From the project root directory:

```bash
# Launch interactive TUI
python3 main.py

# Run direct CLI commands
python3 main.py diff "x^3 + sin(x)" -v x
python3 main.py int "x^2" -l 0 -u 2
python3 main.py lim "sin(x)/x" -p 0
python3 main.py simplify "x + x + 0"
python3 main.py eval "x^2 + y" x=3 y=4
python3 main.py tree "sin(2*x)"
```

#### 2. Running as a Python Module (`python3 -m calculus`)
Because the calculus project files reside in `all-projects/calculus`, set `PYTHONPATH` to include `all-projects` when running module commands:

```bash
# macOS / Linux
PYTHONPATH=all-projects python3 -m calculus

# Or navigate directly into all-projects/
cd all-projects
python3 -m calculus
```

#### 3. Running Unit Tests
```bash
python3 -m pytest
```
