# tests/conftest.py
import os
import sys

# Добавляем корень проекта (на уровень выше папки tests) в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
