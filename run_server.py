#!/usr/bin/env python3
"""
Entry point principal para o Omie MCP Server
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Importar e executar servidor
from src.server import main

if __name__ == "__main__":
    main()