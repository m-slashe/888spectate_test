import pytest
from api.app import create_app
import urllib.parse
from datetime import datetime
from api.entities import EventEntity, EventStatus, EventType, Outcome, SportEntity

class TestApi:

    @pytest.fixture()
    def app(self, mysql):
        app = create_app(db=mysql)
        app.config.update({
            "TESTING": True,
        })

        yield app

    @pytest.fixture()
    def client(self, app):
        return app.test_client()

    @pytest.fixture
    def insert_sport(self, client):
        return client.post('/api/sports/', json={ 'name': 'Name1', 'slug': 'Slug1', 'active': True })

    @pytest.fixture
    def multiple_sports(self, client):
        client.post('/api/sports/', json={ 'name': 'Soccer1', 'slug': 'SSoccer1', 'active': True })
        client.post('/api/sports/', json={ 'name': 'Soccer2', 'slug': 'SSoccer2', 'active': True })
        client.post('/api/sports/', json={ 'name': 'Basketball', 'slug': 'SBasketball', 'active': False })
        client.post('/api/sports/', json={ 'name': 'Tennis', 'slug': 'STennis', 'active': True })
        client.post('/api/sports/', json={ 'name': 'Baseball', 'slug': 'SBaseball', 'active': False })
        client.post('/api/sports/', json={ 'name': 'Golf', 'slug': 'SGolf', 'active': True })

    @pytest.fixture
    def multiple_events(self, client, multiple_sports):
        base_event = {
            'name': 'Event', 
            'slug': 'Slug', 
            'active': True, 
            'type': EventType.InPlay.value, 
            'sport': 1,
            'status': EventStatus.Started.value,
            'scheduled_start': datetime.now(),
            'actual_start': datetime.now()
        }
        event1 = base_event.copy()
        event1.update({ 'name': 'Event 1', 'sport': 2 })
        event2 = base_event.copy()
        event2.update({ 'name': 'Event 2', 'sport': 1 })
        event3 = base_event.copy()
        event3.update({ 'name': 'Event 3', 'sport': 2 })
        event4 = base_event.copy()
        event4.update({ 'name': 'Event 4', 'sport': 1 })
        event5 = base_event.copy()
        event5.update({ 'name': 'Event 5', 'sport': 2 })
        create_url ='/api/events/' 
        client.post(create_url, json=event1)
        client.post(create_url, json=event2)
        client.post(create_url, json=event3)
        client.post(create_url, json=event4)
        client.post(create_url, json=event5)

    @pytest.fixture
    def multiple_selections(self, client, multiple_events):
        base_selection = {
            'name': 'Selection',
            'event': 1,
            'price': 25.50,
            'active': True,
            'outcome': Outcome.Unsettled.value
        }
        selection1 = base_selection.copy()
        selection1.update({ 'name': 'Selection 1', 'event': 2 })
        selection2 = base_selection.copy()
        selection2.update({ 'name': 'Selection 2', 'event': 1 })
        selection3 = base_selection.copy()
        selection3.update({ 'name': 'Selection 3', 'event': 2 })
        selection4 = base_selection.copy()
        selection4.update({ 'name': 'Selection 4', 'event': 1 })
        selection5 = base_selection.copy()
        selection5.update({ 'name': 'Selection 5', 'event': 2 })
        create_url ='/api/selections/' 
        client.post(create_url, json=selection1)
        client.post(create_url, json=selection2)
        client.post(create_url, json=selection3)
        client.post(create_url, json=selection4)
        client.post(create_url, json=selection5)


    @pytest.fixture
    def insert_event(self, client, insert_sport):
        new_event = { 
            'name': 'Event1', 
            'slug': 'Slug1', 
            'active': True, 
            'type': EventType.InPlay.value, 
            'sport': 1,
            'status': EventStatus.Started.value,
            'scheduled_start': datetime.now(),
            'actual_start': datetime.now()
        }
        return client.post('/api/events/', json=new_event)

    @pytest.fixture
    def insert_selection(self, client, insert_event):
        new_selection = {
            'name': 'Selection 1',
            'event': 1,
            'price': 25.50,
            'active': True,
            'outcome': Outcome.Unsettled.value
        }
        return client.post('/api/selections/', json=new_selection)

    def test_should_create_and_return_new_item_with_id(self, insert_sport):
        assert insert_sport.status_code == 200
        assert insert_sport.json == { 'name': 'Name1', 'slug': 'Slug1', 'active': True, 'id': 1 }

    def test_should_update_and_return_updated_item(self, client, insert_sport):
        update_item = { 'name': 'Name Updated', 'slug': 'Slug Updated', 'active': False }
        response = client.put('/api/sports/1', json=update_item)
        assert response.status_code == 200
        update_item_return = update_item.copy()
        update_item_return['id'] = 1
        assert response.json == update_item_return

    def test_should_be_able_to_search_by_sport_name(self, client, multiple_sports):
        response = client.get('/api/sports/?name=Soccer1')
        assert response.status_code == 200
        assert len(response.json['results']) == 1

    def test_should_be_able_to_search_by_multiple_filters(self, client, multiple_sports):
        response = client.get('/api/sports/?name=Soccer&slug=SSoccer1')
        assert response.status_code == 200
        assert len(response.json['results']) == 1
        assert response.json['results'][0] == { 'name': 'Soccer1', 'slug': 'SSoccer1', 'active': True, 'id': 1 }

    def test_should_be_able_to_filter_by_regexp(self, client, multiple_sports):
        url = f'/api/sports/?regexp_name={urllib.parse.quote("B.+l")}'
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.json['results']) == 2

    def test_should_create_event_with_success(self, insert_event):
        assert insert_event.status_code == 200

    def test_should_update_event_with_success(self, client, insert_event):
        update_event = {
            'name': 'Event Updated', 
            'slug': 'Slug Updated', 
            'active': False, 
            'type': EventType.PrePlay.value, 
            'sport': 1,
            'status': EventStatus.Pending.value,
            'scheduled_start': datetime.now(),
            'actual_start': datetime.now()
        }
        response = client.put('/api/events/1', json=update_event)
        assert response.status_code == 200
        update_event.update({ 
            'id': 1, 
            'scheduled_start': update_event['scheduled_start'].strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'actual_start': update_event['actual_start'].strftime('%a, %d %b %Y %H:%M:%S GMT')
        })
        assert response.json == update_event

    def test_should_create_selection_with_success(self, insert_selection):
        assert insert_selection.status_code == 200

    def test_should_update_selection_with_success(self, client, insert_selection):
        update_selection = {
            'name': 'Selection Updated',
            'event': 1,
            'price': 35.50,
            'active': False,
            'outcome': Outcome.Win.value
        }
        response = client.put('/api/selections/1', json=update_selection)
        assert response.status_code == 200
        update_selection.update({
            'id': 1
        })
        assert response.json == update_selection

    def test_should_filter_with_event_active_threshold(self, client, multiple_events):
        response = client.get('/api/sports/?event_active_threshold=3')
        assert response.status_code == 200
        assert len(response.json['results']) == 1
        assert response.json['results'][0] == { 'name': 'Soccer2', 'slug': 'SSoccer2', 'active': True, 'id': 2 }

    def test_should_filter_with_selection_active_threshold(self, client, multiple_selections):
        response = client.get('/api/events/?selection_active_threshold=3')
        assert response.status_code == 200
        assert len(response.json['results']) == 1
        assert response.json['results'][0]['name'] == 'Event 2'

    def test_should_inactivate_sport_while_creating_event_when_all_events_related_becomes_inactivate(self, client, multiple_sports):
        new_event = {
            'name': 'Event Inactivated', 
            'slug': 'Slug', 
            'active': False, 
            'type': EventType.PrePlay.value, 
            'sport': 1,
            'status': EventStatus.Pending.value,
            'scheduled_start': datetime.now(),
            'actual_start': datetime.now()
        }
        response = client.post('/api/events/', json=new_event)
        assert response.status_code == 200
        sport = SportEntity()
        updated_sport = sport.get_by_id(1)
        assert updated_sport.active.value == False

    def test_should_inactivate_sport_while_updating_event_when_all_events_related_becomes_inactivate(self, client, multiple_sports):
        new_event = {
            'name': 'Event Inactivated', 
            'slug': 'Slug', 
            'active': True, 
            'type': EventType.PrePlay.value, 
            'sport': 1,
            'status': EventStatus.Pending.value,
            'scheduled_start': datetime.now(),
            'actual_start': datetime.now()
        }
        response = client.post('/api/events/', json=new_event)
        assert response.status_code == 200
        sport = SportEntity()
        updated_sport = sport.get_by_id(1)
        assert updated_sport.active.value == True
        new_event.update({ 'active': False })
        response = client.put('/api/events/1', json=new_event)
        assert response.status_code == 200
        sport = SportEntity()
        updated_sport = sport.get_by_id(1)
        assert updated_sport.active.value == False

    def test_should_inactivate_event_while_creating_selection_when_all_selections_related_becomes_inactivate(self, client, multiple_events):
        new_selection = {
            'name': 'Selection Inactivated',
            'event': 1,
            'price': 35.50,
            'active': False,
            'outcome': Outcome.Win.value
        }
        response = client.post('/api/selections/', json=new_selection)
        assert response.status_code == 200
        event = EventEntity()
        updated_event = event.get_by_id(1)
        assert updated_event.active.value == False

    def test_should_inactivate_event_while_updating_selection_when_all_selections_related_becomes_inactivate(self, client, multiple_events):
        new_selection = {
            'name': 'Selection Inactivated',
            'event': 1,
            'price': 35.50,
            'active': False,
            'outcome': Outcome.Win.value
        }
        response = client.post('/api/events/', json=new_selection)
        assert response.status_code == 200
        event = EventEntity()
        updated_event = event.get_by_id(1)
        assert updated_event.active.value == True
        new_selection.update({ 'active': False })
        response = client.put('/api/events/1', json=new_selection)
        assert response.status_code == 200
        event = EventEntity()
        updated_event = event.get_by_id(1)
        assert updated_event.active.value == False

