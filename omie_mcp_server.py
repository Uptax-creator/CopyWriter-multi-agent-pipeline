#!/usr/bin/env python3
"""
AVISO: Este arquivo é obsoleto!
Use omie_mcp_server_hybrid.py em seu lugar.

Este arquivo foi substituído pelo servidor híbrido que suporta
tanto STDIO quanto HTTP. Execute:

python3 omie_mcp_server_hybrid.py --mode stdio

"""

import sys
import os

def main():
    print("❌ ARQUIVO OBSOLETO")
    print("Este servidor foi substituído pelo servidor híbrido.")
    print()
    print("🚀 Use em seu lugar:")
    print("python3 omie_mcp_server_hybrid.py --mode stdio")
    print()
    print("Ou para HTTP:")
    print("python3 omie_mcp_server_hybrid.py --mode http")
    
    # Executar servidor híbrido automaticamente
    hybrid_path = os.path.join(os.path.dirname(__file__), "omie_mcp_server_hybrid.py")
    if os.path.exists(hybrid_path):
        print(f"\n🔄 Redirecionando para: {hybrid_path}")
        import subprocess
        subprocess.run([sys.executable, hybrid_path] + sys.argv[1:])
    else:
        print(f"\n❌ Servidor híbrido não encontrado: {hybrid_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()