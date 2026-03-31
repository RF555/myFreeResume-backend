"""
Migration: Update all entries' section_order to the new default.

Also adds empty core_competencies and skill_categories to resume data
if they don't exist.

Usage:
    cd myFreeResume-backend
    .venv/Scripts/python scripts/migrate_section_order.py

Set MONGODB_URI in .env or as environment variable.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from pymongo import AsyncMongoClient

load_dotenv()

MONGODB_URI = os.environ["MONGODB_URI"]
NEW_SECTION_ORDER = [
    "education",
    "core_competencies",
    "skill_categories",
    "skill_highlights",
    "experience",
    "languages",
]


async def migrate():
    client = AsyncMongoClient(MONGODB_URI)
    db = client.get_default_database()

    entries = db.entries
    count = await entries.count_documents({})
    print(f"Found {count} entries to migrate")

    # Update section_order on all entries
    result = await entries.update_many(
        {},
        {
            "$set": {
                "section_order": NEW_SECTION_ORDER,
                "resume.core_competencies": [],
                "resume.skill_categories": [],
            },
        },
    )
    print(f"Updated section_order on {result.modified_count} entries")

    # Update cover_letter: rename subject -> salutation where subject exists
    result2 = await entries.update_many(
        {"cover_letter.subject": {"$exists": True}},
        {
            "$rename": {"cover_letter.subject": "cover_letter.salutation"},
        },
    )
    print(f"Renamed cover_letter.subject -> salutation on {result2.modified_count} entries")

    # Also update resume_profile on users
    users = db.users
    user_count = await users.count_documents({"resume_profile": {"$exists": True}})
    print(f"Found {user_count} users with resume_profile")

    if user_count > 0:
        result3 = await users.update_many(
            {"resume_profile": {"$exists": True}},
            {
                "$set": {
                    "resume_profile.core_competencies": [],
                    "resume_profile.skill_categories": [],
                },
            },
        )
        print(f"Updated {result3.modified_count} user resume profiles")

    client.close()
    print("Migration complete")


if __name__ == "__main__":
    asyncio.run(migrate())
