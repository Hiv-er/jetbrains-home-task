import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def pytest_configure(config):
    results_dir = "allure-results"
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)
