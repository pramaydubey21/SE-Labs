# Software Engineering Labs

**Name:** Pramay Dubey  **SRN:** PES2UG24CS361
**Program:** B.Tech CSE, PES University (EC Campus)

All seven Software Engineering lab submissions, one folder per lab.

| # | Lab | Folder | What's inside |
|---|-----|--------|---------------|
| 1 | Requirements Engineering & UML Use-Case Modelling | [`Lab1_Requirements_UseCase`](Lab1_Requirements_UseCase) | Requirements table, use-case diagram (+ draw.io source), UC-04 flow, for the Freelance Content Creator Escrow Platform |
| 2 | Agile Backlog & Sprint Simulation in Jira | [`Lab2_Jira_Agile_Sprint`](Lab2_Jira_Agile_Sprint) | Epics and user stories with priorities and story points on the FCCEP Jira Scrum board |
| 3 | Software Architecture | [`Lab3_Architecture`](Lab3_Architecture) | Component diagram and microservices architecture justification |
| 4 | LLM Pair-Programming: Arm Wrestle Showdown | [`Lab4_LLM_Pair_Programming`](Lab4_LLM_Pair_Programming) | Pygame game: inverted-push bug fix, AI surge cycle, fatigue warnings, counter-surge bonus; before/after demo clips |
| 5 | Static Code Analysis | [`Lab5_Static_Code_Analysis`](Lab5_Static_Code_Analysis) | Pylint / Flake8 / Bandit reports before and after fixes, issues log, reflection |
| 6 | Code & Branch Coverage | [`Lab6_Code_Branch_Coverage`](Lab6_Code_Branch_Coverage) | 100% line and branch coverage test suites for Bike Share Rental, coverage screenshots |
| 7 | Fuzz Testing | [`Lab7_Fuzz_Testing`](Lab7_Fuzz_Testing) | Hypothesis fuzz tests, fixed parser, lab report |

## Running the code labs

```bash
pip install pygame pytest pytest-cov hypothesis pylint flake8 bandit
python Lab4_LLM_Pair_Programming/main.py
pytest Lab6_Code_Branch_Coverage --cov --cov-branch
pytest Lab7_Fuzz_Testing
```
