from datetime import datetime

class ParkingConfig:
    """ParkingConfig model for system settings"""
    
    def __init__(self, key, value, description=None):
        self.key = key
        self.value = value
        self.description = description
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<ParkingConfig {self.key}>'
