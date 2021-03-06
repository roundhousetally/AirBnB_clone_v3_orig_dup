#!/usr/bin/python3
""" places routes """
from models.place import Place
from models.city import City
from models.user import User
from models.state import State
from models.amenity import Amenity
from models import storage
from api.v1.views import app_views
from flask import jsonify, request


@app_views.route("/cities/<city_id>/places", strict_slashes=False,
                 methods=['GET', 'POST'])
def places(city_id):
    """ /cities/<city_id>/places route """
    place_list = []
    city = storage.get(City, city_id)
    if city is not None:
        places = city.places
        if request.method == 'GET':
            for place in places:
                place_list.append(place.to_dict())
            return jsonify(place_list)
        elif request.method == 'POST':
            try:
                new_dict = request.get_json()
                if 'user_id' not in new_dict.keys():
                    return {"error": "Missing user_id"}, 400
                if 'name' not in new_dict.keys():
                    return {"error": "Missing name"}, 400
                if storage.get(User, new_dict['user_id']) is None:
                    return {"error": "Not found"}, 404
                new_dict.update({'city_id': city_id})
                new_inst = Place(**new_dict)
                new_inst.save()
                return jsonify(new_inst.to_dict()), 201
            except:
                return {"error": "Not a JSON"}, 400
    return {"error": "Not found"}, 404


@app_views.route("/places/<place_id>", strict_slashes=False,
                 methods=['GET', 'DELETE', 'PUT'])
def place_id(place_id):
    """ /places/<place_id> route """
    ignore_list = ["id", "user_id", "city_id", "created_at", "updated_at"]
    place = storage.get(Place, place_id)
    if place is not None:
        if request.method == 'GET':
            return jsonify(place.to_dict())
        elif request.method == 'DELETE':
            storage.delete(place)
            storage.save()
            return {}, 200
        elif request.method == 'PUT':
            try:
                new_dict = request.get_json()
                place_dict = place.to_dict()
                for key, value in new_dict.items():
                    if key not in ignore_list:
                        place_dict.update({key: value})
                storage.delete(place)
                storage.new(Place(**place_dict))
                storage.save()
                return jsonify(place_dict), 200
            except:
                return {"error": "Not a JSON"}, 400
    return {"error": "Not found"}, 404


@app_views.route("/places_search", strict_slashes=False, methods=['POST'])
def places_search():
    """ /places_search route """
    places = storage.all(Place).values()
    places_list = []
    states_list = []
    cities_list = []
    amenities_list = []
    slist = []
    clist = []
    alist = []
    plist = []
    slist_two = []
    clist_two = []
    states_len = 0
    cities_len = 0
    amenities_len = 0
    amenity_exists_list = []
    try:
        new_dict = request.get_json()
    except:
        return {"error": "Not a JSON"}, 400
    if request.headers['Content-Type'] != 'application/json':
        return {"error": "Not a JSON"}, 400
    for place in places:
        places_list.append(place.to_dict())
    if len(new_dict) == 0:
        return jsonify(places_list)
    if 'states' in new_dict:
        states_len = len(new_dict['states'])
        states_list = new_dict['states']
    if 'cities' in new_dict:
        cities_len = len(new_dict['cities'])
        cities_list = new_dict['cities']
    if 'amenities' in new_dict:
        amenities_len = len(new_dict['amenities'])
        amenities_list = new_dict['amenities']
    amenity_list_length = len(amenities_list)
    total_len = states_len + cities_len + amenities_len
    if total_len == 0:
        return jsonify(places_list)
    if states_len > 0:
        for state_id in states_list:
            my_state = storage.get(State, state_id)
            if my_state is not None:
                slist.append(my_state)
        for state in slist:
            for city in state.cities:
                for place in city.places:
                    plist.append(place.to_dict())
    if cities_len > 0:
        for city_id in cities_list:
            my_city = storage.get(City, city_id)
            if my_city is not None:
                clist.append(my_city)
        for city in clist:
            for place in city.places:
                plist.append(place.to_dict())
    if amenities_len > 0:
        if len(plist) == 0:
            for place in places:
                amenity_exists_list = []
                for a in place.amenities:
                    for amenity_id in amenities_list:
                        if a.id == amenity_id:
                            amenity_exists_list.append(1)
                            break
                if len(amenity_exists_list) == amenity_list_length:
                    plist.append(place.to_dict())
        else:
            plist_two = []
            if states_len > 0:
                for state_id in states_list:
                    my_state = storage.get(State, state_id)
                    if my_state is not None:
                        slist_two.append(my_state)
                for state in slist_two:
                    for city in state.cities:
                        for place in city.places:
                            amenity_exists_list = []
                            for a in place.amenities:
                                for amenity_id in amenities_list:
                                    if a.id == amenity_id:
                                        amenity_exists_list.append(1)
                                        break
                            if len(amenity_exists_list) == amenity_list_length:
                                plist_two.append(place.to_dict())
            if cities_len > 0:
                for city_id in cities_list:
                    my_city = storage.get(City, city_id)
                    if my_city is not None:
                        clist_two.append(my_city)
                for city in clist_two:
                    for place in city.places:
                        amenity_exists_list = []
                        for a in place.amenities:
                            for amenity_id in amenities_list:
                                if a.id == amenity_id:
                                    amenity_exists_list.append(1)
                                    break
                        if len(amenity_exists_list) == amenity_list_length:
                            plist_two.append(place.to_dict())
            if len(plist_two) > 0:
                return jsonify(plist_two)
    if len(plist) > 0:
        return jsonify(plist)
    return {"error": "Not found"}, 404
