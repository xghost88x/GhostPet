"""Consistent two-pet desktop presence and persistent friendship state.

The approved Founder remains in PetState, adopted pets remain in adopted_pets.
Older single-pet saves migrate without losing any pet or item data.
"""
from __future__ import annotations

from itertools import combinations

FOUNDER = "founder"
NONE = "none"


def find_adopted(state, pet_id):
    return next((p for p in (state.adopted_pets or [])
                 if isinstance(p, dict) and p.get("id") == pet_id), None)


def valid_id(state, pet_id):
    return pet_id == FOUNDER or find_adopted(state, pet_id) is not None


def active_desktop_ids(state):
    primary = getattr(state, "desktop_pet_id", NONE)
    companion = getattr(state, "desktop_companion_id", NONE)
    result = [primary] if primary != NONE and valid_id(state, primary) else []
    if companion != NONE and companion not in result and valid_id(state, companion):
        result.append(companion)
    return result


def sync_locations(state):
    """Derive locations exclusively from the two saved desktop slots."""
    active = active_desktop_ids(state)
    state.location = "desktop" if FOUNDER in active else "house"
    for pet in (state.adopted_pets or []):
        if isinstance(pet, dict):
            pet["location"] = "desktop" if pet.get("id") in active else "house"
    return active


def repair_presence(state):
    primary = getattr(state, "desktop_pet_id", FOUNDER)
    second = getattr(state, "desktop_companion_id", NONE)
    if primary != NONE and not valid_id(state, primary):
        primary = FOUNDER if state.location == "desktop" else NONE
    # Migrated pre-duo users who sent Founder indoors stay indoors.
    if primary == FOUNDER and state.location != "desktop" and second == NONE:
        primary = NONE
    if second == primary or second == NONE or not valid_id(state, second):
        second = NONE
    if primary == NONE and second != NONE:
        primary, second = second, NONE
    state.desktop_pet_id = primary
    state.desktop_companion_id = second
    sync_locations(state)
    if not isinstance(getattr(state, "relationships", None), dict):
        state.relationships = {}
    return primary


def current_pet(state):
    """None means active Founder, False means no primary desktop pet."""
    primary = state.desktop_pet_id
    if primary == FOUNDER:
        return None
    return find_adopted(state, primary) if primary != NONE else False


def bring_to_desktop(state, pet_id):
    """Make this pet primary; preserve the second pet when possible."""
    if not valid_id(state, pet_id):
        raise ValueError("That pet does not exist.")
    secondary = getattr(state, "desktop_companion_id", NONE)
    if pet_id == secondary:
        old = state.desktop_pet_id
        state.desktop_companion_id = old if old != pet_id else NONE
    elif pet_id == state.desktop_pet_id:
        pass
    else:
        # Keep an existing duo when switching lead to a newly chosen pet.
        state.desktop_companion_id = secondary if secondary != pet_id else NONE
    state.desktop_pet_id = pet_id
    sync_locations(state)
    return None if pet_id == FOUNDER else find_adopted(state, pet_id)


def invite_companion(state, pet_id):
    """Invite one additional pet; never permit more than two active pets."""
    if not valid_id(state, pet_id):
        raise ValueError("That pet does not exist.")
    if state.desktop_pet_id == NONE:
        bring_to_desktop(state, pet_id)
        return False
    if pet_id == state.desktop_pet_id:
        return False
    state.desktop_companion_id = pet_id
    sync_locations(state)
    return True


def send_companion_home(state):
    state.desktop_companion_id = NONE
    sync_locations(state)


def send_desktop_pet_home(state):
    """Send the primary home and promote its buddy, if present."""
    old = state.desktop_pet_id
    state.desktop_pet_id = getattr(state, "desktop_companion_id", NONE)
    state.desktop_companion_id = NONE
    sync_locations(state)
    return old


def all_pet_ids(state):
    return [FOUNDER] + [p["id"] for p in (state.adopted_pets or [])
                        if isinstance(p,dict) and isinstance(p.get("id"),str)]


def pet_name(state, pet_id):
    if pet_id == FOUNDER:
        return state.name
    pet = find_adopted(state, pet_id)
    return pet.get("name", "Buddy") if pet else "Buddy"


def friendship_key(a, b):
    if a == b or a == NONE or b == NONE:
        raise ValueError("Relationship needs two different pets.")
    return "|".join(sorted((a, b)))


def relationship_pairs(state):
    return [(a,b) for a,b in combinations(all_pet_ids(state), 2)]


def relationship_score(state, a, b):
    rel = getattr(state, "relationships", None)
    if not isinstance(rel, dict):
        state.relationships = {}
        rel = state.relationships
    return max(0, min(100, float(rel.get(friendship_key(a,b), 30))))


def strengthen_friendship(state, a, b, points=1.0):
    key = friendship_key(a, b)
    state.relationships[key] = round(
        min(100.0, max(0.0, relationship_score(state,a,b) + points)), 2)
    return state.relationships[key]


def advance_house_friendships(state, hours):
    """Friendship grows quietly while pets share a home, even if house is closed."""
    if hours <= 0:
        return
    indoors = [pid for pid in all_pet_ids(state)
               if pid not in active_desktop_ids(state)]
    for a, b in combinations(indoors, 2):
        strengthen_friendship(state, a, b, min(hours, 24)*.24)


def relationship_title(score):
    if score >= 85:
        return "Best buddies"
    if score >= 60:
        return "Good friends"
    if score >= 35:
        return "Getting closer"
    return "Acquaintances"
