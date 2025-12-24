"""
API Namespaces - Định nghĩa các namespaces cho Swagger documentation
"""
from flask_restx import Namespace, Resource, fields

# Cards Namespace
cards_ns = Namespace('cards', description='Card management operations')

# Card model cho Swagger
card_model = cards_ns.model('Card', {
    'id': fields.String(required=True, description='Card ID'),
    'name': fields.String(description='Owner name'),
    'plate_number': fields.String(description='Vehicle plate'),
    'status': fields.String(enum=['active', 'inactive', 'blocked'], description='Card status'),
    'registered_date': fields.DateTime(description='Registration date'),
    'last_used': fields.DateTime(description='Last time card was used')
})

# Cards List Resource
@cards_ns.route('/')
class CardList(Resource):
    @cards_ns.doc('list_cards')
    @cards_ns.marshal_with(card_model)
    def get(self):
        """Get all registered cards"""
        pass
    
    @cards_ns.doc('create_card')
    @cards_ns.expect(card_model)
    def post(self):
        """Register new card"""
        pass

# Card Detail Resource
@cards_ns.route('/<string:card_id>')
@cards_ns.param('card_id', 'Card ID')
class CardDetail(Resource):
    @cards_ns.doc('get_card')
    def get(self, card_id):
        """Get card details"""
        pass
    
    @cards_ns.doc('update_card')
    def put(self, card_id):
        """Update card info"""
        pass
    
    @cards_ns.doc('delete_card')
    def delete(self, card_id):
        """Delete card"""
        pass

# Card Statistics Resource
@cards_ns.route('/statistics')
class CardStatistics(Resource):
    @cards_ns.doc('get_statistics')
    def get(self):
        """Get card statistics"""
        pass

# Parking Slots Namespace
parking_slots_ns = Namespace('parking_slots', description='Parking slot operations')

parking_slot_model = parking_slots_ns.model('ParkingSlot', {
    'id': fields.Integer(required=True, description='Slot ID'),
    'status': fields.String(enum=['available', 'occupied', 'maintenance'], description='Slot status'),
    'distance': fields.Float(description='Distance to vehicle (cm)'),
    'last_updated': fields.DateTime(description='Last update time')
})

# Parking Slots List Resource
@parking_slots_ns.route('/')
class ParkingSlotList(Resource):
    @parking_slots_ns.doc('list_slots')
    @parking_slots_ns.marshal_with(parking_slot_model)
    def get(self):
        """Get all parking slots status"""
        pass

# Parking Slot Detail Resource
@parking_slots_ns.route('/<int:slot_id>')
@parking_slots_ns.param('slot_id', 'Slot ID')
class ParkingSlotDetail(Resource):
    @parking_slots_ns.doc('get_slot')
    def get(self, slot_id):
        """Get parking slot details"""
        pass

# System Namespace  
system_ns = Namespace('system', description='System information and health checks')

system_info_model = system_ns.model('SystemInfo', {
    'status': fields.String(description='System status'),
    'version': fields.String(description='System version'),
    'uptime': fields.Float(description='System uptime in seconds'),
    'total_slots': fields.Integer(description='Total parking slots'),
    'available_slots': fields.Integer(description='Available slots'),
})

# System Info Resource
@system_ns.route('/info')
class SystemInfo(Resource):
    @system_ns.doc('get_system_info')
    @system_ns.marshal_with(system_info_model)
    def get(self):
        """Get system information"""
        pass

# System Health Check Resource
@system_ns.route('/health')
class SystemHealth(Resource):
    @system_ns.doc('health_check')
    def get(self):
        """Health check endpoint"""
        pass

