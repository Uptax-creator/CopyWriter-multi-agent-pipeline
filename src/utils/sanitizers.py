"""
Sanitizadores para dados JSON e texto
"""

import re
import json
from typing import Any, Dict, List, Union, Optional
from src.utils.logger import logger

class JSONSanitizer:
    """Classe para sanitização de dados JSON"""
    
    @staticmethod
    def remove_emojis(text: str) -> str:
        """Remove emojis de texto"""
        if not isinstance(text, str):
            return text
        
        # Padrão para remover emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        
        return emoji_pattern.sub(r'', text)
    
    @staticmethod
    def sanitize_string(text: str) -> str:
        """Sanitizar string para uso em JSON"""
        if not isinstance(text, str):
            return str(text)
        
        # Remove emojis
        text = JSONSanitizer.remove_emojis(text)
        
        # Remove caracteres de controle
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
        
        # Normaliza espaços
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitizar dicionário recursivamente"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        
        for key, value in data.items():
            # Sanitizar chave
            clean_key = JSONSanitizer.sanitize_string(str(key))
            
            # Sanitizar valor
            if isinstance(value, str):
                sanitized[clean_key] = JSONSanitizer.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[clean_key] = JSONSanitizer.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[clean_key] = JSONSanitizer.sanitize_list(value)
            else:
                sanitized[clean_key] = value
        
        return sanitized
    
    @staticmethod
    def sanitize_list(data: List[Any]) -> List[Any]:
        """Sanitizar lista recursivamente"""
        if not isinstance(data, list):
            return data
        
        sanitized = []
        
        for item in data:
            if isinstance(item, str):
                sanitized.append(JSONSanitizer.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(JSONSanitizer.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(JSONSanitizer.sanitize_list(item))
            else:
                sanitized.append(item)
        
        return sanitized
    
    @staticmethod
    def sanitize_json(data: Any) -> Any:
        """Sanitizar dados JSON de qualquer tipo"""
        if isinstance(data, str):
            return JSONSanitizer.sanitize_string(data)
        elif isinstance(data, dict):
            return JSONSanitizer.sanitize_dict(data)
        elif isinstance(data, list):
            return JSONSanitizer.sanitize_list(data)
        else:
            return data
    
    @staticmethod
    def safe_json_dumps(data: Any, **kwargs) -> str:
        """JSON dumps seguro com sanitização"""
        try:
            # Sanitizar dados
            sanitized_data = JSONSanitizer.sanitize_json(data)
            
            # Configurações padrão
            default_kwargs = {
                'ensure_ascii': False,
                'indent': 2,
                'separators': (',', ': ')
            }
            
            # Mesclar com kwargs fornecidos
            final_kwargs = {**default_kwargs, **kwargs}
            
            return json.dumps(sanitized_data, **final_kwargs)
            
        except Exception as e:
            logger.error(f"Erro ao serializar JSON: {e}")
            return json.dumps({"error": "Erro na serialização JSON"})
    
    @staticmethod
    def safe_json_loads(text: str) -> Any:
        """JSON loads seguro com tratamento de erros"""
        try:
            # Sanitizar texto
            clean_text = JSONSanitizer.sanitize_string(text)
            
            # Parse JSON
            data = json.loads(clean_text)
            
            # Sanitizar dados parseados
            return JSONSanitizer.sanitize_json(data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON: {e}")
            return {"error": f"JSON inválido: {str(e)}"}
        except Exception as e:
            logger.error(f"Erro inesperado no parse JSON: {e}")
            return {"error": f"Erro inesperado: {str(e)}"}

class TextSanitizer:
    """Classe para sanitização de texto"""
    
    @staticmethod
    def clean_cnpj(cnpj: str) -> str:
        """Limpar CNPJ mantendo apenas números"""
        if not cnpj:
            return ""
        
        return re.sub(r'[^0-9]', '', str(cnpj))
    
    @staticmethod
    def clean_cpf(cpf: str) -> str:
        """Limpar CPF mantendo apenas números"""
        if not cpf:
            return ""
        
        return re.sub(r'[^0-9]', '', str(cpf))
    
    @staticmethod
    def clean_phone(phone: str) -> str:
        """Limpar telefone mantendo apenas números"""
        if not phone:
            return ""
        
        return re.sub(r'[^0-9]', '', str(phone))
    
    @staticmethod
    def clean_cep(cep: str) -> str:
        """Limpar CEP mantendo apenas números"""
        if not cep:
            return ""
        
        return re.sub(r'[^0-9]', '', str(cep))
    
    @staticmethod
    def format_currency(value: Union[str, int, float]) -> str:
        """Formatar valor monetário"""
        try:
            if isinstance(value, str):
                # Remove caracteres não numéricos exceto vírgula e ponto
                value = re.sub(r'[^0-9,.]', '', value)
                # Converte vírgula para ponto
                value = value.replace(',', '.')
            
            float_value = float(value)
            return f"{float_value:.2f}"
            
        except (ValueError, TypeError):
            return "0.00"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 255) -> str:
        """Truncar texto para comprimento máximo"""
        if not text:
            return ""
        
        text = str(text)
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length-3] + "..."
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalizar nome próprio"""
        if not name:
            return ""
        
        # Remove caracteres especiais
        name = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', str(name))
        
        # Normaliza espaços
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Capitaliza palavras
        words = name.split()
        normalized_words = []
        
        for word in words:
            if len(word) > 2:
                # Palavras maiores que 2 caracteres: primeira letra maiúscula
                normalized_words.append(word.capitalize())
            else:
                # Palavras pequenas: minúsculas (exceto primeira palavra)
                if not normalized_words:
                    normalized_words.append(word.capitalize())
                else:
                    normalized_words.append(word.lower())
        
        return " ".join(normalized_words)

# Instâncias globais
json_sanitizer = JSONSanitizer()
text_sanitizer = TextSanitizer()