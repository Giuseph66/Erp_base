"""
Testes unitários para validadores do sistema ERP.
Casos críticos: validação de entrada, formatos e regras de negócio.
"""
import pytest
from datetime import datetime, date


class TestEmailValidator:
    """Testes para validação de e-mail."""

    def test_valid_email(self):
        """Deve aceitar e-mails válidos."""
        from backend.src.validators import validate_email
        
        valid_emails = [
            "usuario@exemplo.com",
            "nome.sobrenome@empresa.com.br",
            "user+tag@domain.org"
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True

    def test_invalid_email(self):
        """Deve rejeitar e-mails inválidos."""
        from backend.src.validators import validate_email
        
        invalid_emails = [
            "invalido",
            "@exemplo.com",
            "usuario@",
            "usuario@exemplo",
            ""
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False

    def test_email_none(self):
        """Deve lidar com None gracefully."""
        from backend.src.validators import validate_email
        assert validate_email(None) is False


class TestCPFCNPJValidator:
    """Testes para validação de CPF e CNPJ."""

    def test_valid_cpf(self):
        """Deve aceitar CPFs válidos."""
        from backend.src.validators import validate_cpf
        
        # CPFs válidos de teste
        assert validate_cpf("12345678909") is True
        assert validate_cpf("11144477735") is True

    def test_invalid_cpf(self):
        """Deve rejeitar CPFs inválidos."""
        from backend.src.validators import validate_cpf
        
        invalid_cpfs = [
            "12345678900",  # Dígito verificador inválido
            "11111111111",  # Todos iguais
            "00000000000",
            "12345678",     # Tamanho incorreto
            "",
            None
        ]
        
        for cpf in invalid_cpfs:
            assert validate_cpf(cpf) is False

    def test_valid_cnpj(self):
        """Deve aceitar CNPJs válidos."""
        from backend.src.validators import validate_cnpj
        
        assert validate_cnpj("12345678000195") is True

    def test_invalid_cnpj(self):
        """Deve rejeitar CNPJs inválidos."""
        from backend.src.validators import validate_cnpj
        
        invalid_cnpjs = [
            "12345678000190",  # Dígito verificador inválido
            "11111111111111",  # Todos iguais
            "12345678",        # Tamanho incorreto
            ""
        ]
        
        for cnpj in invalid_cnpjs:
            assert validate_cnpj(cnpj) is False


class TestDateValidator:
    """Testes para validação de datas."""

    def test_valid_date_string(self):
        """Deve aceitar datas em formato válido."""
        from backend.src.validators import validate_date
        
        assert validate_date("2024-01-15") is True
        assert validate_date("15/01/2024") is True

    def test_invalid_date_string(self):
        """Deve rejeitar datas inválidas."""
        from backend.src.validators import validate_date
        
        invalid_dates = [
            "2024-13-01",  # Mês inválido
            "2024-02-30",  # Dia inválido
            "invalido",
            ""
        ]
        
        for date_str in invalid_dates:
            assert validate_date(date_str) is False

    def test_date_in_future(self):
        """Deve validar se data está no futuro quando necessário."""
        from backend.src.validators import validate_date_not_in_future
        
        past_date = "2020-01-01"
        future_date = "2099-01-01"
        
        assert validate_date_not_in_future(past_date) is True
        assert validate_date_not_in_future(future_date) is False


class TestNumericValidators:
    """Testes para validadores numéricos."""

    def test_positive_number(self):
        """Deve validar números positivos."""
        from backend.src.validators import validate_positive_number
        
        assert validate_positive_number(10) is True
        assert validate_positive_number(0.5) is True
        assert validate_positive_number(0) is False
        assert validate_positive_number(-5) is False

    def test_number_range(self):
        """Deve validar números dentro de um intervalo."""
        from backend.src.validators import validate_number_range
        
        assert validate_number_range(5, min_val=0, max_val=10) is True
        assert validate_number_range(-1, min_val=0, max_val=10) is False
        assert validate_number_range(11, min_val=0, max_val=10) is False

    def test_decimal_precision(self):
        """Deve validar precisão decimal."""
        from backend.src.validators import validate_decimal_precision
        
        assert validate_decimal_precision(10.50, max_decimals=2) is True
        assert validate_decimal_precision(10.555, max_decimals=2) is False


class TestStringValidators:
    """Testes para validadores de string."""

    def test_required_field(self):
        """Deve validar campos obrigatórios."""
        from backend.src.validators import validate_required
        
        assert validate_required("valor") is True
        assert validate_required("") is False
        assert validate_required(None) is False
        assert validate_required("   ") is False

    def test_min_max_length(self):
        """Deve validar comprimento mínimo e máximo."""
        from backend.src.validators import validate_length
        
        assert validate_length("abc", min_len=1, max_len=5) is True
        assert validate_length("", min_len=1, max_len=5) is False
        assert validate_length("abcdef", min_len=1, max_len=5) is False

    def test_alphanumeric(self):
        """Deve validar strings alfanuméricas."""
        from backend.src.validators import validate_alphanumeric
        
        assert validate_alphanumeric("abc123") is True
        assert validate_alphanumeric("abc-123") is False
        assert validate_alphanumeric("") is False
