"""
Custom exceptions for QuoteWise AI application.
Provides structured error handling with specific exception types.
"""

from typing import Optional, Dict, Any


class QuoteWiseException(Exception):
    """Base exception for QuoteWise AI application."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        super().__init__(self.message)


class ProductNotFoundError(QuoteWiseException):
    """Raised when a product is not found in inventory."""
    pass


class InsufficientStockError(QuoteWiseException):
    """Raised when requested quantity exceeds available stock."""
    pass


class PricingCalculationError(QuoteWiseException):
    """Raised when pricing calculation fails."""
    pass


class AgentExecutionError(QuoteWiseException):
    """Raised when agent execution fails."""
    pass


class PDFGenerationError(QuoteWiseException):
    """Raised when PDF generation fails."""
    pass


class ConfigurationError(QuoteWiseException):
    """Raised when configuration is invalid."""
    pass


class APIError(QuoteWiseException):
    """Raised when external API calls fail."""
    pass


class ValidationError(QuoteWiseException):
    """Raised when data validation fails."""
    pass

