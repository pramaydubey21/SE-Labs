# SE Lab 5: Static Code Analysis

**Name:** Pramay Dubey
**SRN:** PES2UG24CS361
**Assigned repo:** SETAPESU26/L5_54_warehouse-stock
**File:** `warehouse_stock_manager.py`

Static analysis of a warehouse stock manager using **Pylint**, **Flake8** and **Bandit**, followed by fixing every reported issue plus the logic bugs found by running the program.

## Results

| Tool | Before | After |
|---|---|---|
| Pylint | 37 messages, 4.48/10 | 0 messages, **10.00/10** |
| Flake8 | 19 violations | 0 |
| Bandit | 5 issues (1 High, 2 Medium, 2 Low) | No issues identified |

## Repository contents

| File | Contents |
|---|---|
| `warehouse_stock_manager.py` | Cleaned and fixed program |
| `issues.md` | Issue table: what was found and how it was fixed |
| `reflection.md` | Answers to the reflection questions |
| `pylint_report.txt`, `flake8_report.txt`, `bandit_report.txt` | Tool reports for the fixed file |
| `run_output.txt` | Output of the fixed program |
| `reports_before_fix/` | Original program, its output and the original tool reports |

## Running

```bash
# The supervisor password is read from an environment variable
WH_SUPERVISOR_PASSWORD=wh-admin-1234 python3 warehouse_stock_manager.py

python3 -m pip install pylint bandit flake8
python3 -m pylint warehouse_stock_manager.py > pylint_report.txt
python3 -m bandit -r warehouse_stock_manager.py > bandit_report.txt
python3 -m flake8 warehouse_stock_manager.py > flake8_report.txt
```
