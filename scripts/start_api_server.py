#!/usr/bin/env python3
"""Start the API server with lazy loading for better memory management"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.api_server import start_api_server

if __name__ == '__main__':
    start_api_server() 