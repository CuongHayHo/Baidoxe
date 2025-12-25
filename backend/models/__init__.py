"""
Data models module
"""
# db will be created and assigned by app.py
db = None

# User model will be created dynamically by app.py after db initialization
User = None

# Import other models
from .card import Card
from .card_log import CardLog
from .parking_slot import ParkingSlot
from .parking_config import ParkingConfig

__all__ = ['db', 'User', 'Card', 'CardLog', 'ParkingSlot', 'ParkingConfig']