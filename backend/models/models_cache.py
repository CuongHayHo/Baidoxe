"""
Database models cache - Cache SQLAlchemy models to avoid recreating them
"""

_models_cache = {}

def get_sqlalchemy_models():
    """
    Get cached SQLAlchemy models, or create them if not cached
    
    Returns:
        Tuple of (UserModel, CardModel, CardLogModel, ParkingSlotModel, ParkingConfigModel)
    """
    global _models_cache
    
    if not _models_cache:
        # First time - create and cache models
        from scripts.init_db import create_sqlalchemy_models
        UserModel, CardModel, CardLogModel, ParkingSlotModel, ParkingConfigModel = create_sqlalchemy_models()
        
        _models_cache = {
            'UserModel': UserModel,
            'CardModel': CardModel,
            'CardLogModel': CardLogModel,
            'ParkingSlotModel': ParkingSlotModel,
            'ParkingConfigModel': ParkingConfigModel
        }
    
    return (
        _models_cache['UserModel'],
        _models_cache['CardModel'],
        _models_cache['CardLogModel'],
        _models_cache['ParkingSlotModel'],
        _models_cache['ParkingConfigModel']
    )

def clear_models_cache():
    """Clear the models cache (use only for testing)"""
    global _models_cache
    _models_cache = {}
