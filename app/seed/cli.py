"""
CLI script for seeding templates.
"""
import sys

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.seed.seed_templates import seed_templates


def main():
    """Main CLI entry point."""
    force = "--force" in sys.argv
    
    db: Session = SessionLocal()
    try:
        result = seed_templates(db, force=force)
        print(f"Seeding complete!")
        print(f"  Templates created: {result['templates_created']}")
        print(f"  Templates skipped: {result['templates_skipped']}")
        print(f"  Versions created: {result['versions_created']}")
        print(f"  Versions skipped: {result['versions_skipped']}")
    except Exception as e:
        print(f"Error seeding templates: {e}", file=sys.stderr)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

