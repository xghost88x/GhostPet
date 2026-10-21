"""Keep a single visible desktop pet without replacing the Founder save.

Original companions remain in PetState; adopted housemates remain independent
dictionaries in PetState.adopted_pets. This module is Qt-free and unit-tested.
"""
from __future__ import annotations

FOUNDER = "founder"
NONE = "none"


def find_adopted(state, pet_id):
    return next(
        (pet for pet in (state.adopted_pets or [])
         if isinstance(pet, dict) and pet.get("id") == pet_id),
        None,
    )


def repair_presence(state):
    """Migrate saved households without changing names, stats, positions or coins."""
    current = getattr(state, "desktop_pet_id", FOUNDER)
    if current != FOUNDER and find_adopted(state, current) is None:
        current = FOUNDER if state.location == "desktop" else NONE
    if current == FOUNDER and state.location != "desktop":
        current = NONE  # Founder deliberately indoors on an old save.
    if current not in (FOUNDER, NONE):
        state.location = "house"
    for pet in state.adopted_pets or []:
        pet["location"] = ("desktop" if pet.get("id") == current else "house")
    state.desktop_pet_id = current
    return current


def current_pet(state):
    """Return None for the founder, a housemate dict, or False for an empty desktop."""
    pet_id = state.desktop_pet_id
    if pet_id == FOUNDER:
        return None if state.location == "desktop" else False
    if pet_id == NONE:
        return False
    pet = find_adopted(state, pet_id)
    return pet if pet is not None and pet.get("location") == "desktop" else False


def bring_to_desktop(state, pet_id):
    """Summon a pet, returning its associated record (None means Founder)."""
    if pet_id != FOUNDER and find_adopted(state, pet_id) is None:
        raise ValueError("That pet no longer exists in your nursery.")
    state.location = "desktop" if pet_id == FOUNDER else "house"
    for pet in state.adopted_pets or []:
        pet["location"] = "desktop" if pet.get("id") == pet_id else "house"
    state.desktop_pet_id = pet_id
    return None if pet_id == FOUNDER else find_adopted(state, pet_id)


def send_desktop_pet_home(state):
    """Send only the displayed pet indoors; the founder save stays untouched."""
    pet_id = state.desktop_pet_id
    if pet_id == FOUNDER:
        state.location = "house"
    else:
        selected = find_adopted(state, pet_id)
        if selected is not None:
            selected["location"] = "house"
    state.desktop_pet_id = NONE
    return pet_id
