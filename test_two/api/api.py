from flask import Blueprint, request
from api.logger import logger
from api.entities import EventEntity, SelectionEntity, SportEntity
from api.events import EventCreated, EventUpdated, SelectionCreated, SelectionUpdated, dispatch_event

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
sports_blueprint = Blueprint('sports', __name__, url_prefix='/sports')
events_blueprint = Blueprint('events', __name__, url_prefix='/events')
selections_blueprint = Blueprint('selections', __name__, url_prefix='/selections')

api_blueprint.register_blueprint(sports_blueprint)
api_blueprint.register_blueprint(events_blueprint)
api_blueprint.register_blueprint(selections_blueprint)

@sports_blueprint.route("/", methods=['GET'])
def get_sports():
    sport_entity = SportEntity()
    if len(list(request.args.values())) > 0:
        result = sport_entity.get_by_filter(request.args)        
    else:
        result = sport_entity.get_all()
    return { 'results': result }
    
@sports_blueprint.route("/", methods=['POST'])
def create_sports():
    sport_entity = SportEntity()
    sport_entity.update_by_json(request.json)
    sport_entity.create()
    return sport_entity.to_json()

@sports_blueprint.route("/<id>", methods=["PUT"])
def update_sports(id: int):
    sport_entity = SportEntity()
    sport = sport_entity.get_by_id(id)
    sport.update_by_json(request.json)
    sport.update()    
    return sport.to_json()

@events_blueprint.route("/", methods=['GET'])
def get_events():
    event_entity = EventEntity()
    if len(list(request.args.values())) > 0:
        result = event_entity.get_by_filter(request.args)        
    else:
        result = event_entity.get_all()
    return { 'results': result }

@events_blueprint.route("/", methods=['POST'])
def create_events():
    event_entity = EventEntity()
    event_entity.update_by_json(request.json)
    event_entity.create()
    event_json = event_entity.to_json()
    dispatch_event(EventCreated, event_json)
    return event_json

@events_blueprint.route("/<id>", methods=['PUT'])
def update_events(id):
    event_entity = EventEntity()
    event = event_entity.get_by_id(id)
    event.update_by_json(request.json)
    event.update()
    event_json = event.to_json()
    dispatch_event(EventUpdated, event_json)
    return event_json

@selections_blueprint.route("/", methods=['GET'])
def get_selections():
    selection_entity = SelectionEntity()
    if len(list(request.args.values())) > 0:
        result = selection_entity.get_by_filter(request.args)        
    else:
        result = selection_entity.get_all()
    return { 'results': result }

@selections_blueprint.route("/", methods=['POST'])
def create_selections():
    selection_entity = SelectionEntity()
    selection_entity.update_by_json(request.json)
    selection_entity.create()
    selection_json = selection_entity.to_json()
    dispatch_event(SelectionCreated, selection_json)
    return selection_json

@selections_blueprint.route("/<id>", methods=['PUT'])
def update_selections(id: int):
    selection_entity = SelectionEntity()
    selection = selection_entity.get_by_id(id)
    selection.update_by_json(request.json)
    selection.update()
    selection_json = selection.to_json()
    dispatch_event(SelectionUpdated, selection_json)
    return selection_json

@selections_blueprint.route("/<id>", methods=['DELETE'])
def delete_selections(id: int):
    selection_entity = SelectionEntity()
    selection = selection_entity.get_by_id(id)
    selection.delete()
    return { 'message': 'selection record deleted with success!' }