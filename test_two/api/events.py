from typing import Type

from api.entities import EventEntity, SelectionEntity, SportEntity


class SystemEvent:
    pass

class EventCreated(SystemEvent):
    pass

class EventUpdated(SystemEvent):
    pass

class SelectionCreated(SystemEvent):
    pass

class SelectionUpdated(SystemEvent):
    pass

registered_callbacks = []

def dispatch_event(event_type: Type[SystemEvent], params):
    for registered_callback in registered_callbacks:
        if registered_callback['event'] == event_type:
            registered_callback['callback'](params)

def register_event(type: Type[SystemEvent], callback):
    registered_callbacks.append({ 'event': type, 'callback': callback })

def update_sports_on_event_change(params):
    event_entity = EventEntity()
    results = event_entity.get_by_filter({ 'sport': params['sport'] })
    if not any(result['active'] for result in results):
        sport_entity = SportEntity()
        sport = sport_entity.get_by_id(params['sport'])
        sport.active.set(False)
        sport.update()

def update_events_on_selection_change(params):
    selection_entity = SelectionEntity()
    results = selection_entity.get_by_filter({ 'event': params['event'] })
    if not any(result['active'] for result in results):
        event_entity = EventEntity()
        event = event_entity.get_by_id(params['event'])
        event.active.set(False)
        event.update()

register_event(EventCreated, update_sports_on_event_change)
register_event(EventUpdated, update_sports_on_event_change)
register_event(SelectionCreated, update_events_on_selection_change)
register_event(SelectionUpdated, update_events_on_selection_change)