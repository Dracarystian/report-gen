from abc import ABC, abstractmethod

class BaseIntegration(ABC):
    """Clase base que todas las integraciones deben implementar."""
    
    def __init__(self, config):
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    def verify_connection(self):
        """Verifica la conexión con la API."""
        pass
    
    @abstractmethod
    def fetch_data(self, **kwargs):
        """Obtiene datos de la API para generar el informe."""
        pass
    
    @abstractmethod
    def generate_report_data(self, **kwargs):
        """Prepara los datos para el informe."""
        pass
    
    def __str__(self):
        return f"{self.name} Integration"