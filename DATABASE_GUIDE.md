# Complete Database Guide for 1ne.ai Backend
## From Beginner to Expert - Step by Step

**Table of Contents:**
1. [What is a Database?](#1-what-is-a-database)
2. [PostgreSQL Basics](#2-postgresql-basics)
3. [SQLAlchemy ORM Introduction](#3-sqlalchemy-orm-introduction)
4. [Your Project's Database Setup](#4-your-projects-database-setup)
5. [Understanding Models (Tables)](#5-understanding-models-tables)
6. [Database Relationships](#6-database-relationships)
7. [Working with Sessions](#7-working-with-sessions)
8. [Querying Data](#8-querying-data)
9. [Creating and Updating Records](#9-creating-and-updating-records)
10. [Database Migrations with Alembic](#10-database-migrations-with-alembic)
11. [Advanced Concepts](#11-advanced-concepts)
12. [Best Practices](#12-best-practices)

---

## 1. What is a Database?

### 1.1 Basic Concept

Think of a **database** like a digital filing cabinet:
- **Tables** = Drawers in the cabinet
- **Rows** = Individual files/documents
- **Columns** = Information fields on each file (like name, date, etc.)

**Example from Real Life:**
```
Library Database:
├── Books Table
│   ├── Row 1: "Python Guide", Author: "John", ISBN: "12345"
│   ├── Row 2: "Database Basics", Author: "Jane", ISBN: "67890"
│   └── ...
├── Authors Table
│   ├── Row 1: Name: "John", Country: "USA"
│   └── ...
└── Borrowers Table
    └── ...
```

### 1.2 Why Use a Database?

1. **Persistent Storage**: Data survives when your app restarts
2. **Structured Data**: Organized in tables with relationships
3. **Fast Queries**: Find data quickly even with millions of records
4. **Data Integrity**: Rules ensure data is valid and consistent
5. **Concurrent Access**: Multiple users can access data simultaneously

### 1.3 Types of Databases

- **Relational (SQL)**: Data in tables with relationships (PostgreSQL, MySQL)
- **NoSQL**: Document-based, key-value, etc. (MongoDB, Redis)

**Your project uses PostgreSQL** - a powerful relational database.

---

## 2. PostgreSQL Basics

### 2.1 What is PostgreSQL?

PostgreSQL is a **relational database management system (RDBMS)**. It's:
- **Open-source** and free
- **ACID compliant** (Atomicity, Consistency, Isolation, Durability)
- **Highly reliable** and feature-rich
- **Supports JSON** (which your project uses extensively)

### 2.2 Key PostgreSQL Concepts

#### **Tables**
A table is a collection of related data organized in rows and columns.

```sql
-- Example: templates table structure
templates
├── id (UUID) - unique identifier
├── slug (String) - unique URL-friendly name
├── name (String) - display name
├── description (Text) - longer description
├── category (Enum) - type of template
├── is_active (Boolean) - whether it's active
└── created_at (DateTime) - when created
```

#### **Primary Key**
A unique identifier for each row. In your project, every table uses `id` as primary key (UUID type).

#### **Foreign Key**
A reference to another table's primary key. Creates relationships between tables.

**Example from your project:**
- `template_versions.template_id` → references `templates.id`
- This creates a link: "This version belongs to that template"

#### **Indexes**
Speed up queries. Like an index in a book - helps find data quickly.

**In your project:**
```python
id = Column(UUID(as_uuid=True), primary_key=True, index=True)
slug = Column(String(100), unique=True, nullable=False, index=True)
```
- `id` is indexed (fast lookups by ID)
- `slug` is indexed (fast lookups by slug)

### 2.3 Data Types in PostgreSQL

Your project uses these types:

| Type | Purpose | Example |
|------|---------|---------|
| **UUID** | Unique identifier | `550e8400-e29b-41d4-a716-446655440000` |
| **String/VARCHAR** | Text (limited length) | `"lesson_planner"` |
| **Text** | Long text (unlimited) | `"This is a long description..."` |
| **Integer** | Whole numbers | `5`, `100` |
| **Boolean** | True/False | `True`, `False` |
| **DateTime** | Date and time | `2024-01-15 10:30:00` |
| **JSON** | Structured data | `{"key": "value", "array": [1,2,3]}` |
| **Numeric** | Decimal numbers | `0.000123` (for cost_estimate) |
| **Enum** | Fixed set of values | `"draft"`, `"published"`, `"archived"` |

---

## 3. SQLAlchemy ORM Introduction

### 3.1 What is an ORM?

**ORM = Object-Relational Mapping**

Instead of writing raw SQL like this:
```sql
SELECT * FROM templates WHERE slug = 'lesson_planner';
```

You write Python code:
```python
template = db.query(Template).filter(Template.slug == 'lesson_planner').first()
```

**Benefits:**
- Write Python instead of SQL
- Type-safe (IDE can help you)
- Database-agnostic (works with PostgreSQL, MySQL, etc.)
- Prevents SQL injection attacks

### 3.2 SQLAlchemy Basics

**SQLAlchemy** is the Python ORM your project uses.

**Key Components:**

1. **Engine**: Connection to the database
2. **Session**: Active connection for queries
3. **Models**: Python classes representing database tables
4. **Queries**: Methods to fetch/update data

---

## 4. Your Project's Database Setup

### 4.1 Project Structure

```
app/
├── db/
│   ├── base.py          # Base class for all models
│   └── session.py       # Database session management
├── models/
│   ├── template.py              # Template model
│   ├── template_version.py      # TemplateVersion model
│   └── template_execution.py   # TemplateExecution model
└── core/
    └── config.py        # Database URL configuration
```

### 4.2 Database Connection String

**Location:** `app/core/config.py`

```python
DATABASE_URL: str = "postgresql://user:password@localhost:5432/1ne_db"
```

**Breaking it down:**
- `postgresql://` - Protocol (PostgreSQL)
- `user:password` - Database credentials
- `@localhost:5432` - Server address and port
- `/1ne_db` - Database name

**In production:** This comes from environment variables (`.env` file).

### 4.3 Database Engine Setup

**Location:** `app/db/session.py`

```python
from sqlalchemy import create_engine

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Check connection before using
    echo=settings.ENVIRONMENT == "dev",  # Print SQL queries in dev mode
)
```

**What this does:**
- Creates a connection pool (reuses connections efficiently)
- `pool_pre_ping`: Tests connections before using (prevents stale connections)
- `echo=True`: In dev mode, prints all SQL queries (great for debugging!)

### 4.4 Base Model Class

**Location:** `app/db/base.py`

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass
```

**Why this exists:**
- All your models inherit from `Base`
- SQLAlchemy uses this to track all models
- Alembic (migrations) uses this to discover models

**Model Discovery:**
```python
# Import all models here so Alembic can discover them
from app.models.template import Template
from app.models.template_version import TemplateVersion
from app.models.template_execution import TemplateExecution
```

This tells Alembic: "These are all the tables in the database."

---

## 5. Understanding Models (Tables)

### 5.1 What is a Model?

A **model** is a Python class that represents a database table. Each instance of the class is a row in the table.

### 5.2 Template Model - Deep Dive

**Location:** `app/models/template.py`

```python
class Template(Base):
    """Template model representing a system template."""
    
    __tablename__ = "templates"  # Actual table name in database
    
    # Columns
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    # ... more columns
```

**Breaking it down:**

#### **`__tablename__`**
- The actual table name in PostgreSQL
- If not specified, SQLAlchemy uses the class name (lowercase)

#### **Column Definitions**

**1. Primary Key:**
```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
```
- `UUID(as_uuid=True)`: PostgreSQL UUID type, Python gets UUID object
- `primary_key=True`: This is the unique identifier
- `default=uuid.uuid4`: Auto-generate UUID when creating new record
- `index=True`: Create index for fast lookups

**2. Unique String:**
```python
slug = Column(String(100), unique=True, nullable=False, index=True)
```
- `String(100)`: Max 100 characters
- `unique=True`: No two rows can have the same slug
- `nullable=False`: This field is required (cannot be NULL)
- `index=True`: Fast lookups by slug

**3. Text Field:**
```python
description = Column(Text, nullable=True)
```
- `Text`: Unlimited length (vs String which has limit)
- `nullable=True`: Can be empty/NULL

**4. Boolean:**
```python
is_active = Column(Boolean, default=True, nullable=False)
```
- `Boolean`: True or False
- `default=True`: New records default to True
- `nullable=False`: Must have a value

**5. JSON Field:**
```python
grade_bands_supported = Column(JSON, nullable=True)
```
- `JSON`: Stores JSON data (arrays, objects)
- Example value: `["3-5", "6-8", "9-12"]`
- PostgreSQL can query inside JSON!

**6. Enum:**
```python
category = Column(SQLEnum(TemplateCategory, values_callable=lambda x: [e.value for e in x]), nullable=False)
```
- `SQLEnum`: Fixed set of allowed values
- `TemplateCategory`: Python enum with values like `LESSON_DESIGN`, `ASSESSMENT`
- Database stores as string: `"lesson_design"`, `"assessment"`

**7. DateTime with Auto-update:**
```python
created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```
- `created_at`: Set once when record is created
- `updated_at`: Updates automatically whenever record is modified
- `datetime.utcnow`: Current UTC time

### 5.3 TemplateVersion Model

**Key Features:**

#### **Foreign Key:**
```python
template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False, index=True)
```
- `ForeignKey("templates.id")`: References `templates` table's `id` column
- `ondelete="CASCADE"`: If template is deleted, delete all its versions
- Creates relationship: "This version belongs to that template"

#### **Unique Constraint:**
```python
__table_args__ = (
    UniqueConstraint("template_id", "version", name="uq_template_version"),
)
```
- Ensures: One template can't have two versions with the same version number
- Example: Template A can have version 1, 2, 3, but not two version 1s

#### **Relationship:**
```python
template = relationship("Template", backref="versions")
```
- `template`: Access parent Template object
- `backref="versions"`: Template gets `.versions` attribute (list of versions)

**Usage:**
```python
version = db.query(TemplateVersion).first()
print(version.template.name)  # Access parent template

template = db.query(Template).first()
print(template.versions)  # List of all versions (from backref)
```

### 5.4 TemplateExecution Model

**Purpose:** Audit trail - tracks every time a template is executed.

**Key Features:**

#### **Multiple Foreign Keys:**
```python
template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id", ondelete="CASCADE"), ...)
template_version_id = Column(UUID(as_uuid=True), ForeignKey("template_versions.id", ondelete="SET NULL"), ...)
```
- Links to both Template AND TemplateVersion
- `ondelete="SET NULL"`: If version deleted, set this to NULL (keep execution record)

#### **JSON Columns for Flexible Data:**
```python
input_data = Column(JSON, nullable=False)   # What user sent
output_data = Column(JSON, nullable=True)   # What LLM returned
token_usage = Column(JSON, nullable=True)   # {"prompt": 370, "completion": 228, "total": 598}
```

**Why JSON?**
- Flexible schema (can store different structures)
- No need to create new columns for new fields
- Perfect for API request/response data

---

## 6. Database Relationships

### 6.1 Types of Relationships

Your project uses these relationships:

#### **One-to-Many (1:N)**
- **Template → TemplateVersion**: One template has many versions
- **Template → TemplateExecution**: One template has many executions

#### **Many-to-One (N:1)**
- **TemplateVersion → Template**: Many versions belong to one template
- **TemplateExecution → Template**: Many executions belong to one template

### 6.2 Understanding Foreign Keys

**Foreign Key = Reference to another table**

**Example:**
```
templates table:
id: 550e8400-e29b-41d4-a716-446655440000
slug: "lesson_planner"
name: "Lesson Planner"

template_versions table:
id: 660e8400-e29b-41d4-a716-446655440001
template_id: 550e8400-e29b-41d4-a716-446655440000  ← Foreign Key
version: 1
```

The `template_id` in `template_versions` points to `templates.id`.

### 6.3 Cascade Behaviors

**`ondelete="CASCADE"`:**
```python
template_id = Column(..., ForeignKey("templates.id", ondelete="CASCADE"), ...)
```
- If template is deleted → all its versions are deleted
- If template is deleted → all its executions are deleted

**`ondelete="SET NULL"`:**
```python
template_version_id = Column(..., ForeignKey("template_versions.id", ondelete="SET NULL"), ...)
```
- If version is deleted → execution's `template_version_id` becomes NULL
- Execution record is kept (for audit trail)

### 6.4 Relationship Navigation

**Using Relationships:**

```python
# Get template and access its versions
template = db.query(Template).filter(Template.slug == "lesson_planner").first()
versions = template.versions  # List of TemplateVersion objects

# Get version and access its template
version = db.query(TemplateVersion).first()
parent_template = version.template  # Template object
```

**In Your Project:**
```python
# From routes_templates.py
def _get_latest_published_version(db: Session, template_id: Any) -> Optional[TemplateVersion]:
    return (
        db.query(TemplateVersion)
        .filter(
            TemplateVersion.template_id == template_id,
            TemplateVersion.status == TemplateVersionStatus.PUBLISHED,
        )
        .order_by(TemplateVersion.version.desc())
        .first()
    )
```

---

## 7. Working with Sessions

### 7.1 What is a Session?

A **session** is your active connection to the database. It's like a transaction - you do work, then commit or rollback.

### 7.2 Session Lifecycle

**Location:** `app/db/session.py`

```python
def get_db() -> Generator[Session, None, None]:
    """Dependency function for FastAPI to get database session."""
    db = SessionLocal()  # Create new session
    try:
        yield db          # Give session to your code
        db.commit()      # Save changes (if no errors)
    except Exception:
        db.rollback()    # Undo changes (if error occurred)
        raise
    finally:
        db.close()       # Always close session
```

**Step by step:**
1. **Create session**: `db = SessionLocal()`
2. **Use session**: Query, create, update records
3. **Commit**: `db.commit()` - saves changes permanently
4. **Rollback**: `db.rollback()` - undoes changes if error
5. **Close**: `db.close()` - releases connection back to pool

### 7.3 Using Sessions in FastAPI

**In your API endpoints:**

```python
from app.db.session import get_db
from sqlalchemy.orm import Session

@router.get("/api/v1/templates")
def list_templates(
    db: Session = Depends(get_db),  # FastAPI injects session here
):
    # Use db to query
    templates = db.query(Template).all()
    return templates
```

**How it works:**
- FastAPI calls `get_db()` when request arrives
- `get_db()` creates session and yields it
- Your endpoint code uses `db`
- When endpoint finishes, `get_db()` commits and closes

### 7.4 Session Best Practices

**✅ DO:**
- Let FastAPI manage sessions (use `Depends(get_db)`)
- Commit explicitly when needed: `db.commit()`
- Handle errors with try/except

**❌ DON'T:**
- Create sessions manually (unless necessary)
- Forget to close sessions (FastAPI does this automatically)
- Share sessions across requests (each request gets its own)

---

## 8. Querying Data

### 8.1 Basic Queries

#### **Get All Records:**
```python
templates = db.query(Template).all()
# Returns: List of all Template objects
```

#### **Get One Record:**
```python
template = db.query(Template).first()
# Returns: First Template object, or None if empty
```

#### **Get by ID:**
```python
template = db.query(Template).filter(Template.id == template_id).first()
```

#### **Get by Slug (from your project):**
```python
template = db.query(Template).filter(
    Template.slug == slug,
    Template.is_active.is_(True)
).first()
```

### 8.2 Filtering

#### **Simple Filter:**
```python
# Find active templates
active_templates = db.query(Template).filter(Template.is_active == True).all()
```

#### **Multiple Filters:**
```python
# AND condition (both must be true)
template = db.query(Template).filter(
    Template.slug == slug,
    Template.is_active.is_(True)
).first()
```

#### **OR Condition:**
```python
from sqlalchemy import or_

templates = db.query(Template).filter(
    or_(
        Template.category == TemplateCategory.LESSON_DESIGN,
        Template.category == TemplateCategory.ASSESSMENT
    )
).all()
```

#### **Comparison Operators:**
```python
# Greater than
versions = db.query(TemplateVersion).filter(
    TemplateVersion.version > 5
).all()

# Contains (for strings)
templates = db.query(Template).filter(
    Template.name.contains("lesson")
).all()

# In (check if value in list)
templates = db.query(Template).filter(
    Template.category.in_([TemplateCategory.LESSON_DESIGN, TemplateCategory.ASSESSMENT])
).all()
```

### 8.3 Advanced Queries from Your Project

#### **Subquery (Complex Example):**

**Location:** `app/api/v1/routes_templates.py`

```python
# Find templates that have at least one published version
subquery = (
    db.query(TemplateVersion.template_id)
    .filter(TemplateVersion.status == TemplateVersionStatus.PUBLISHED)
    .distinct()  # Remove duplicates
    .subquery()  # Convert to subquery
)

query = db.query(Template).filter(
    Template.is_active.is_(True),
    Template.id.in_(subquery),  # Template ID must be in subquery results
)
```

**What this does:**
1. Subquery finds all template_ids that have published versions
2. Main query finds templates whose ID is in that list
3. Result: Only active templates with published versions

#### **Ordering:**
```python
# Order by version descending (newest first)
latest_version = (
    db.query(TemplateVersion)
    .filter(TemplateVersion.template_id == template_id)
    .order_by(TemplateVersion.version.desc())
    .first()
)
```

#### **JSON Queries:**
```python
# Query JSON column (PostgreSQL feature)
templates = db.query(Template).filter(
    Template.grade_bands_supported.contains(["3-5"])
).all()
```

### 8.4 Counting and Aggregations

```python
# Count records
count = db.query(Template).count()

# Count with filter
active_count = db.query(Template).filter(
    Template.is_active == True
).count()
```

### 8.5 Limiting Results

```python
# Get first 10
templates = db.query(Template).limit(10).all()

# Skip first 5, get next 10 (pagination)
templates = db.query(Template).offset(5).limit(10).all()
```

---

## 9. Creating and Updating Records

### 9.1 Creating New Records

#### **Method 1: Create Object, Add, Commit**

**From your project:** `app/services/execution_service.py`

```python
execution = TemplateExecution(
    template_id=template.id,
    template_version_id=template_version.id,
    template_version=template_version.version,
    user_id=user_id,
    tenant_id=tenant_id,
    input_data=input_data,
    output_data=universal_output.model_dump(),
    model_used=model_used,
    provider_used=provider_used,
    token_usage=token_usage_dict,
    cost_estimate=cost_estimate,
    latency_ms=latency_ms,
    cache_hit=False,
)

db.add(execution)      # Add to session (not saved yet)
db.commit()            # Save to database
db.refresh(execution)  # Reload from database (gets auto-generated fields like id)
```

**Step by step:**
1. **Create object**: `execution = TemplateExecution(...)`
2. **Add to session**: `db.add(execution)` - tells SQLAlchemy to track this
3. **Commit**: `db.commit()` - actually saves to database
4. **Refresh**: `db.refresh(execution)` - reloads from DB (gets `id`, `created_at`, etc.)

#### **Method 2: Using Constructor**

```python
template = Template(
    slug="new_template",
    name="New Template",
    category=TemplateCategory.LESSON_DESIGN,
    is_active=True,
)
db.add(template)
db.commit()
```

### 9.2 Updating Records

#### **Method 1: Modify Object, Commit**

```python
# Get existing record
template = db.query(Template).filter(Template.slug == "lesson_planner").first()

# Modify
template.is_active = False
template.description = "Updated description"

# Save
db.commit()
```

**Note:** `updated_at` auto-updates because of `onupdate=datetime.utcnow` in model!

#### **Method 2: Bulk Update**

```python
# Update multiple records at once
db.query(Template).filter(
    Template.category == TemplateCategory.ASSESSMENT
).update({"is_active": False})
db.commit()
```

### 9.3 Deleting Records

```python
# Delete one record
template = db.query(Template).filter(Template.slug == "old_template").first()
if template:
    db.delete(template)
    db.commit()
```

**Cascade Behavior:**
- If you delete a Template, all its TemplateVersions are deleted (CASCADE)
- All TemplateExecutions for that template are also deleted (CASCADE)

### 9.4 Transaction Management

**What is a Transaction?**
- A group of database operations that either all succeed or all fail
- Example: Transfer money - debit one account, credit another (both must succeed)

**In Your Project:**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()      # All operations succeed → commit
    except Exception:
        db.rollback()    # Error occurred → undo all changes
        raise
    finally:
        db.close()
```

**Manual Transaction:**
```python
try:
    # Create template
    template = Template(...)
    db.add(template)
    
    # Create version
    version = TemplateVersion(...)
    db.add(version)
    
    # Both succeed → commit
    db.commit()
except Exception:
    # Error → rollback (neither is saved)
    db.rollback()
    raise
```

---

## 10. Database Migrations with Alembic

### 10.1 What are Migrations?

**Migrations** are scripts that change your database schema (add tables, columns, etc.).

**Why use migrations?**
- Version control for database structure
- Apply changes consistently across environments (dev, staging, prod)
- Rollback if something goes wrong

### 10.2 Alembic Overview

**Alembic** is the migration tool your project uses (made by SQLAlchemy team).

**Key Concepts:**
- **Revision**: A migration script (like a git commit)
- **Upgrade**: Apply migration (forward)
- **Downgrade**: Undo migration (backward)

### 10.3 Your Project's Migration Setup

**Location:** `alembic/env.py`

```python
from app.db.base import Base
from app.core.config import settings

# Set database URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Tell Alembic about your models
target_metadata = Base.metadata
```

**How Alembic finds models:**
- `Base.metadata` contains all models that inherit from `Base`
- Models are imported in `app/db/base.py` (so Alembic can see them)

### 10.4 Migration File Structure

**Location:** `alembic/versions/001_create_template_models.py`

```python
revision: str = '001_create_template_models'
down_revision: Union[str, None] = None  # This is the first migration

def upgrade() -> None:
    """Apply this migration - create tables."""
    op.create_table('templates', ...)
    op.create_table('template_versions', ...)
    op.create_table('template_executions', ...)

def downgrade() -> None:
    """Undo this migration - drop tables."""
    op.drop_table('template_executions')
    op.drop_table('template_versions')
    op.drop_table('templates')
```

**Key Operations:**
- `op.create_table()`: Create new table
- `op.drop_table()`: Delete table
- `op.add_column()`: Add column to table
- `op.drop_column()`: Remove column
- `op.create_index()`: Create index
- `op.create_foreign_key()`: Create foreign key

### 10.5 Common Migration Commands

```bash
# Create new migration (auto-detect changes)
alembic revision --autogenerate -m "add new column"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# See current migration version
alembic current

# See migration history
alembic history
```

### 10.6 Creating a New Migration

**Example: Add a new column to Template**

1. **Modify model:**
```python
# app/models/template.py
class Template(Base):
    # ... existing columns ...
    new_field = Column(String(50), nullable=True)  # Add this
```

2. **Generate migration:**
```bash
alembic revision --autogenerate -m "add new_field to templates"
```

3. **Review generated file:**
```python
# alembic/versions/002_add_new_field.py
def upgrade():
    op.add_column('templates', sa.Column('new_field', sa.String(length=50), nullable=True))

def downgrade():
    op.drop_column('templates', 'new_field')
```

4. **Apply migration:**
```bash
alembic upgrade head
```

### 10.7 Migration Best Practices

**✅ DO:**
- Always review auto-generated migrations
- Test migrations on dev database first
- Keep migrations small and focused
- Write both upgrade and downgrade functions

**❌ DON'T:**
- Edit old migrations (create new ones instead)
- Skip testing migrations
- Delete migration files (they're history!)

---

## 11. Advanced Concepts

### 11.1 Eager Loading (Reducing Queries)

**Problem: N+1 Query Problem**

```python
# BAD: Makes many queries
templates = db.query(Template).all()
for template in templates:
    print(template.versions)  # New query for each template!
```

**Solution: Eager Loading**

```python
from sqlalchemy.orm import joinedload

# GOOD: One query with JOIN
templates = db.query(Template).options(
    joinedload(Template.versions)
).all()
for template in templates:
    print(template.versions)  # Already loaded, no new query!
```

### 11.2 Query Optimization

#### **Use Indexes:**
Your models already have indexes on frequently queried columns:
```python
id = Column(..., index=True)      # Fast lookups by ID
slug = Column(..., index=True)    # Fast lookups by slug
```

#### **Select Only Needed Columns:**
```python
# Instead of loading entire object
template = db.query(Template).filter(Template.id == id).first()

# Load only specific columns
result = db.query(Template.id, Template.name).filter(Template.id == id).first()
```

### 11.3 Raw SQL (When Needed)

Sometimes you need raw SQL:

```python
from sqlalchemy import text

result = db.execute(text("SELECT COUNT(*) FROM templates WHERE is_active = true"))
count = result.scalar()
```

**Use sparingly** - prefer ORM when possible.

### 11.4 Database Indexes

**What are indexes?**
- Data structure that speeds up queries
- Like an index in a book - helps find pages quickly

**In your project:**
```python
id = Column(UUID(as_uuid=True), primary_key=True, index=True)
slug = Column(String(100), unique=True, nullable=False, index=True)
created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
```

**When to add indexes:**
- Columns used in WHERE clauses frequently
- Foreign keys (usually auto-indexed)
- Columns used for sorting (ORDER BY)

**Trade-off:**
- Indexes speed up reads
- Indexes slow down writes (must update index)
- Don't over-index!

### 11.5 JSON Queries in PostgreSQL

Your project uses JSON columns. PostgreSQL can query inside JSON:

```python
# Check if JSON array contains value
templates = db.query(Template).filter(
    Template.grade_bands_supported.contains(["3-5"])
).all()

# Access nested JSON (PostgreSQL syntax)
# Example: input_data = {"user": {"name": "John"}}
# Can query: input_data->'user'->>'name'
```

### 11.6 Soft Deletes

**Soft delete** = Mark as deleted instead of actually deleting.

**In your project:**
```python
is_active = Column(Boolean, default=True, nullable=False)
```

**Usage:**
```python
# "Delete" (soft)
template.is_active = False
db.commit()

# Query only active
templates = db.query(Template).filter(Template.is_active == True).all()
```

**Benefits:**
- Can recover "deleted" records
- Maintains audit trail
- No cascade delete issues

### 11.7 Database Connection Pooling

**What is pooling?**
- Reuse database connections instead of creating new ones
- Improves performance

**In your project:**
```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Test connection before using
)
```

**How it works:**
- Pool maintains set of connections
- Request gets connection from pool
- Request finishes, connection returns to pool
- Next request reuses connection

---

## 12. Best Practices

### 12.1 Model Design

**✅ DO:**
- Use UUIDs for primary keys (better than auto-increment integers)
- Add indexes on frequently queried columns
- Use appropriate data types (String vs Text)
- Set defaults for common fields
- Use nullable=True for optional fields

**❌ DON'T:**
- Create too many indexes (slows writes)
- Use Text for short strings (use String with limit)
- Forget to set nullable=False for required fields

### 12.2 Query Best Practices

**✅ DO:**
- Use filters to limit results
- Use `.first()` when you only need one result
- Use eager loading to avoid N+1 queries
- Add indexes for frequently filtered columns

**❌ DON'T:**
- Load all records when you only need a few
- Make queries in loops (N+1 problem)
- Forget to handle None results

### 12.3 Transaction Management

**✅ DO:**
- Let FastAPI manage sessions (use `Depends(get_db)`)
- Commit explicitly when needed
- Use try/except for error handling
- Rollback on errors

**❌ DON'T:**
- Create sessions manually (unless necessary)
- Forget to commit changes
- Leave transactions open

### 12.4 Migration Best Practices

**✅ DO:**
- Review auto-generated migrations
- Test migrations before applying
- Write both upgrade and downgrade
- Keep migrations small

**❌ DON'T:**
- Edit old migrations
- Skip testing
- Create migrations for data changes (use scripts instead)

### 12.5 Security

**✅ DO:**
- Use parameterized queries (SQLAlchemy does this automatically)
- Validate input data
- Use environment variables for database credentials
- Limit database user permissions

**❌ DON'T:**
- Use string concatenation for SQL (SQL injection risk)
- Store credentials in code
- Give database user unnecessary permissions

---

## Quick Reference

### Common Query Patterns

```python
# Get by ID
obj = db.query(Model).filter(Model.id == id).first()

# Get all
all_objs = db.query(Model).all()

# Filter
filtered = db.query(Model).filter(Model.field == value).all()

# Create
new_obj = Model(field1=value1, field2=value2)
db.add(new_obj)
db.commit()

# Update
obj.field = new_value
db.commit()

# Delete
db.delete(obj)
db.commit()

# Count
count = db.query(Model).count()

# Order
ordered = db.query(Model).order_by(Model.field.desc()).all()
```

### Your Project's Models

```
Template (1) ──< (many) TemplateVersion
Template (1) ──< (many) TemplateExecution
TemplateVersion (1) ──< (many) TemplateExecution
```

### Key Files

- **Models**: `app/models/*.py`
- **Session**: `app/db/session.py`
- **Base**: `app/db/base.py`
- **Config**: `app/core/config.py`
- **Migrations**: `alembic/versions/*.py`

---

## Practice Exercises

### Exercise 1: Basic Query
Write a function that gets all active templates with published versions.

**Solution:**
```python
def get_active_templates_with_published_versions(db: Session):
    subquery = (
        db.query(TemplateVersion.template_id)
        .filter(TemplateVersion.status == TemplateVersionStatus.PUBLISHED)
        .distinct()
        .subquery()
    )
    return db.query(Template).filter(
        Template.is_active == True,
        Template.id.in_(subquery)
    ).all()
```

### Exercise 2: Create Record
Write a function that creates a new template with a version.

**Solution:**
```python
def create_template_with_version(db: Session, slug: str, name: str):
    template = Template(
        slug=slug,
        name=name,
        category=TemplateCategory.LESSON_DESIGN,
        is_active=True
    )
    db.add(template)
    db.flush()  # Get template.id without committing
    
    version = TemplateVersion(
        template_id=template.id,
        version=1,
        status=TemplateVersionStatus.DRAFT,
        input_schema={"type": "object", "properties": {}}
    )
    db.add(version)
    db.commit()
    db.refresh(template)
    return template
```

### Exercise 3: Update Record
Write a function that publishes a template version.

**Solution:**
```python
def publish_version(db: Session, template_id: uuid.UUID, version: int):
    version_obj = db.query(TemplateVersion).filter(
        TemplateVersion.template_id == template_id,
        TemplateVersion.version == version
    ).first()
    
    if version_obj:
        version_obj.status = TemplateVersionStatus.PUBLISHED
        version_obj.published_at = datetime.utcnow()
        db.commit()
        return version_obj
    return None
```

---

## Conclusion

You now understand:
- ✅ What databases are and why we use them
- ✅ PostgreSQL basics and data types
- ✅ SQLAlchemy ORM and how it works
- ✅ Your project's database structure
- ✅ How to query, create, update, and delete records
- ✅ Database relationships and foreign keys
- ✅ Migrations with Alembic
- ✅ Advanced concepts and best practices

**Next Steps:**
1. Read through your project's models again with this knowledge
2. Trace through API endpoints to see how they use the database
3. Try writing your own queries
4. Experiment with creating/updating records
5. Practice writing migrations

**Remember:** The best way to learn is by doing. Try modifying queries, creating new records, and understanding how data flows through your application!

---

*Happy coding! 🚀*

