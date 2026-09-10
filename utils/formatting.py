def format_venue(building, room):
    if building and room:
        return f"{building} • {room}"
    return "Venue: Unassigned"
