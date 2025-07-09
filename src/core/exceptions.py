#!/usr/bin/env python3
"""
Exceções customizadas para o projeto Omie MCP
"""


class OmieException(Exception):
    """Exceção base para erros da API Omie"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(message)


class OmieAPIError(OmieException):
    """Erro da API Omie"""
    def __init__(self, fault_code: str, fault_string: str):
        self.fault_code = fault_code
        self.fault_string = fault_string
        super().__init__(f"Erro Omie [{fault_code}]: {fault_string}", fault_code)


class OmieConnectionError(OmieException):
    """Erro de conexão com a API Omie"""
    pass


class OmieAuthenticationError(OmieException):
    """Erro de autenticação com a API Omie"""
    pass


class OmieValidationError(OmieException):
    """Erro de validação de dados"""
    pass


class MCPError(Exception):
    """Exceção base para erros do MCP"""
    def __init__(self, message: str, code: int = -32000):
        self.message = message
        self.code = code
        super().__init__(message)


class MCPInvalidRequestError(MCPError):
    """Erro de requisição MCP inválida"""
    def __init__(self, message: str = "Invalid request"):
        super().__init__(message, -32600)


class MCPMethodNotFoundError(MCPError):
    """Erro de método MCP não encontrado"""
    def __init__(self, message: str = "Method not found"):
        super().__init__(message, -32601)


class MCPInvalidParamsError(MCPError):
    """Erro de parâmetros MCP inválidos"""
    def __init__(self, message: str = "Invalid params"):
        super().__init__(message, -32602)


class MCPInternalError(MCPError):
    """Erro interno do MCP"""
    def __init__(self, message: str = "Internal error"):
        super().__init__(message, -32603)