# Tenderd API Tests

[![GitHub CI](https://github.com/prashanth-sams/tenderd-api-tests/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/prashanth-sams/tenderd-api-tests/actions/workflows/main.yml)

## Overview

- **Previous Test Run Artifacts**: [View results](https://github.com/prashanth-sams/tenderd-api-tests/actions/runs/16884551434)  
- **Trigger a New Test Run**: [Run via GitHub Actions](https://github.com/prashanth-sams/tenderd-api-tests/actions/workflows/main.yml)  
- **HTML Test Reports** (my custom reporting lib): [View reports](https://github.com/prashanth-sams/tenderd-api-tests/tree/main/report)  
- **Recorded Test Execution Video**: [Watch video](https://github.com/prashanth-sams/tenderd-api-tests/blob/main/API%20Test%20Execution.mov)  

---

## Prerequisites

- Python 3.x (tested on 3.9/3.10)
- `pipenv`

### Install Libraries and Activate Virtual Environment
```bash
sudo pip3 install pipenv
pipenv install --python /usr/bin/python3
pipenv shell
```

### Install libraries from `Pipfile.lock` (Optional)
```
pipenv install --ignore-pipfile
```

## Test Execution
Try any of the below cmds to execute the tests

| Runner        | Command                       |
| ---           | ---                           |
| pytest        | `pytest ./tests`              |
|               | `pytest -m smoke --reruns 1`  |
|               | `python3 -m pytest ./tests`   |
| task runner   | `invoke tests`                |
| pipeenv       | `pipenv run pytest`           |
