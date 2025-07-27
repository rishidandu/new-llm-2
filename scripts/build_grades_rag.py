#!/usr/bin/env python3
"""Build RAG system with ASU grades data only"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import build_rag
from config.settings import Config

if __name__ == "__main__":
    config = Config()
    print("Building RAG system with ASU grades data...")
    build_rag(config, ["asu_grades"])
    print("RAG system built successfully with ASU grades data!") 