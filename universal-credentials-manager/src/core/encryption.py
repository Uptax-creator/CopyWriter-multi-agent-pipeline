"""
🔐 Sistema de Criptografia Universal
Gerenciamento seguro de criptografia para credenciais
"""

import os
import base64
import logging
from typing import Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json

logger = logging.getLogger("encryption")

class EncryptionManager:
    """Gerenciador de criptografia para credenciais"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.cipher = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Inicializa sistema de criptografia para o projeto"""
        # Senha mestre específica do projeto
        env_var = f"UCM_{self.project_name.upper().replace('-', '_')}_PASSWORD"
        master_password = os.getenv(env_var, f"ucm-{self.project_name}-default-2025")
        
        # Gerar chave de criptografia
        password = master_password.encode()
        salt = f"ucm-{self.project_name}-salt-2025".encode()[:16].ljust(16, b'0')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.cipher = Fernet(key)
        
        logger.info(f"🔒 Criptografia inicializada para projeto: {self.project_name}")
    
    def encrypt_data(self, data: Dict[str, Any]) -> str:
        """Criptografa dados sensíveis"""
        try:
            json_data = json.dumps(data, ensure_ascii=False)
            encrypted_data = self.cipher.encrypt(json_data.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_data).decode('ascii')
        except Exception as e:
            logger.error(f"❌ Erro ao criptografar dados: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """Descriptografa dados sensíveis"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode('ascii'))
            decrypted_data = self.cipher.decrypt(decoded_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            logger.error(f"❌ Erro ao descriptografar dados: {e}")
            raise
    
    def test_encryption(self) -> bool:
        """Testa se a criptografia está funcionando"""
        try:
            test_data = {"test": "encryption_working", "number": 12345}
            encrypted = self.encrypt_data(test_data)
            decrypted = self.decrypt_data(encrypted)
            
            success = test_data == decrypted
            if success:
                logger.info(f"✅ Teste de criptografia passou para {self.project_name}")
            else:
                logger.error(f"❌ Teste de criptografia falhou para {self.project_name}")
            
            return success
        except Exception as e:
            logger.error(f"❌ Erro no teste de criptografia: {e}")
            return False

class MultiProjectEncryption:
    """Gerenciador de criptografia para múltiplos projetos"""
    
    def __init__(self):
        self.encryptors: Dict[str, EncryptionManager] = {}
    
    def get_encryptor(self, project_name: str) -> EncryptionManager:
        """Obtém ou cria encriptador para um projeto"""
        if project_name not in self.encryptors:
            self.encryptors[project_name] = EncryptionManager(project_name)
        
        return self.encryptors[project_name]
    
    def test_all_projects(self) -> Dict[str, bool]:
        """Testa criptografia de todos os projetos"""
        results = {}
        
        for project_name, encryptor in self.encryptors.items():
            results[project_name] = encryptor.test_encryption()
        
        return results

# Instância global
multi_project_encryption = MultiProjectEncryption()