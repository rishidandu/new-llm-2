#!/usr/bin/env python3
"""Build RAG system"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import build_rag
from config.settings import Config

if __name__ == "__main__":
    config = Config()
    build_rag(config, ["asu_web", "reddit", "asu_grades"])
