def validate_faculty(data):

    required = [
        "faculty_id",
        "username",
        "email",
        "contact",
        "password"
    ]

    for field in required:

        if not data.get(field):

            return f"{field} is required."

    return None

def validate_allocation(data):

    required = [

        "faculty_id",

        "subject_code",

        "batch"

    ]

    for field in required:

        if not data.get(field):

            return f"{field} is required."

    return None