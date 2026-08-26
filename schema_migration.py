"""Small, idempotent SQLite migrations for development databases."""


FACULTY_COLUMNS = (
    "faculty_id",
    "username",
    "email",
    "contact",
    "cabin_no",
    "password_hash",
    "role",
    "professor_post",
    "special_role",
)


def _rebuild_faculty_for_nullable_import_fields(db, columns):
    nullable_fields = {
        "email",
        "contact",
        "password_hash",
        "professor_post",
        "special_role",
    }
    needs_rebuild = any(
        field not in columns or columns[field][3]
        for field in nullable_fields
    )
    if not needs_rebuild:
        return

    select_parts = []
    for field in FACULTY_COLUMNS:
        if field in columns:
            expression = f'"{field}"'
        elif field == "special_role":
            expression = "'None'"
        elif field == "role":
            expression = "'faculty'"
        else:
            expression = "NULL"
        select_parts.append(expression)

    db.session.execute(db.text("PRAGMA foreign_keys=OFF"))
    db.session.execute(db.text(
        """
        CREATE TABLE faculty_new (
            faculty_id VARCHAR(20) NOT NULL PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            contact VARCHAR(15),
            cabin_no VARCHAR(50),
            password_hash VARCHAR(255),
            role VARCHAR(20) NOT NULL DEFAULT 'faculty',
            professor_post VARCHAR(80),
            special_role VARCHAR(30) DEFAULT 'None'
        )
        """
    ))
    db.session.execute(db.text(
        "INSERT INTO faculty_new (" + ", ".join(FACULTY_COLUMNS) + ") "
        "SELECT " + ", ".join(select_parts) + " FROM faculty"
    ))
    db.session.execute(db.text("DROP TABLE faculty"))
    db.session.execute(db.text("ALTER TABLE faculty_new RENAME TO faculty"))
    db.session.execute(db.text("PRAGMA foreign_keys=ON"))


def migrate_schema(db):
    """Apply only additive or nullability-preserving schema changes."""

    columns = {
        row[1]: row
        for row in db.session.execute(
            db.text("PRAGMA table_info(faculty)")
        ).fetchall()
    }
    if columns:
        _rebuild_faculty_for_nullable_import_fields(db, columns)
    allocation_columns = {
        row[1]: row
        for row in db.session.execute(
            db.text("PRAGMA table_info(faculty_allocations)")
        ).fetchall()
    }
    if allocation_columns and (
        allocation_columns.get("batch", (None, None, None, 0))[3]
        or allocation_columns.get("slot", (None, None, None, 0))[3]
    ):
        db.session.execute(db.text("PRAGMA foreign_keys=OFF"))
        db.session.execute(db.text("""
            CREATE TABLE faculty_allocations_new (
                id INTEGER PRIMARY KEY,
                faculty_id VARCHAR(20) NOT NULL,
                subject_code VARCHAR(20) NOT NULL,
                subject_name VARCHAR(100) NOT NULL,
                slot VARCHAR(255),
                class_type VARCHAR(20) NOT NULL DEFAULT 'theory',
                batch INTEGER,
                section VARCHAR(20),
                room_number VARCHAR(50),
                building_name VARCHAR(100),
                FOREIGN KEY(faculty_id) REFERENCES faculty(faculty_id)
            )
        """))
        db.session.execute(db.text("""
            INSERT INTO faculty_allocations_new
            (id, faculty_id, subject_code, subject_name, slot, class_type,
             batch, section, room_number, building_name)
            SELECT id, faculty_id, subject_code, subject_name, slot, class_type,
                   batch, section, room_number, building_name
            FROM faculty_allocations
        """))
        db.session.execute(db.text("DROP TABLE faculty_allocations"))
        db.session.execute(db.text(
            "ALTER TABLE faculty_allocations_new RENAME TO faculty_allocations"
        ))
        db.session.execute(db.text("PRAGMA foreign_keys=ON"))
    db.session.commit()