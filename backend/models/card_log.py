from datetime import datetime

class CardLog:
    """CardLog model for tracking card entry/exit"""
    
    def __init__(self, card_number, action, timestamp=None, location=None, 
                 parking_slot=None, duration_minutes=None, calculated_fee=None, notes=None):
        self.card_number = card_number
        self.action = action  # 'in' or 'out'
        self.timestamp = timestamp or datetime.utcnow()
        self.location = location
        self.parking_slot = parking_slot
        self.duration_minutes = duration_minutes
        self.calculated_fee = calculated_fee
        self.notes = notes
    
    def __repr__(self):
        return f'<CardLog {self.card_number} {self.action}>'
