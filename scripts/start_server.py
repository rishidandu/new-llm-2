#!/usr/bin/env python3
"""Start web server"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import start_server, build_rag
from config.settings import Config

if __name__ == "__main__":
    config = Config()
    rag_system = build_rag(config, ["asu_web", "reddit", "asu_grades"])
    start_server(config, rag_system)
