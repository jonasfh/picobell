# Setup Development Environment

To replace Thonny, we use a local virtual environment with `mpremote`.

## 1. Create Virtual Environment

```bash
cd pico
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Usage

### List files on Pico
```bash
mpremote ls
```

### Upload source code
```bash
mpremote cp -r src/* :
```

### Enter REPL
```bash
mpremote repl
```

### Run tests on device
```bash
mpremote run tests/test_hw.py
```

### Soft Reset
```bash
mpremote soft-reset
```
