# utils/validators.py
import re

def validar_password(password):
    """Validar fortaleza de contraseña"""
    pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return bool(re.match(pattern, password))

def validar_email(email):
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validar_codigo_barras(codigo):
    """Validar código de barras (solo numérico, 8-13 dígitos)"""
    return codigo.isdigit() and 8 <= len(codigo) <= 13