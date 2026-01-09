# SQLModel Relationships

Detailed guide to defining relationships between SQLModel tables.

## One-to-Many Relationship

A parent can have multiple children (e.g., Team has many Members).

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    headquarters: str

    # The "many" side - list of related objects
    members: List["Member"] = Relationship(back_populates="team")


class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str

    # Foreign key - links to parent
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")

    # The "one" side - single related object
    team: Optional[Team] = Relationship(back_populates="members")
```

### Usage

```python
# Create team with members
team = Team(name="Engineering", headquarters="Building A")
member1 = Member(name="Alice", role="Developer", team=team)
member2 = Member(name="Bob", role="Designer", team=team)

session.add(team)
session.add(member1)
session.add(member2)
session.commit()

# Query
team = session.get(Team, 1)
for member in team.members:
    print(member.name)
```

## Many-to-Many Relationship

Both sides can have multiple related objects (e.g., Books and Authors).

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

# Link table - MUST be defined first
class BookAuthorLink(SQLModel, table=True):
    book_id: Optional[int] = Field(
        default=None, foreign_key="book.id", primary_key=True
    )
    author_id: Optional[int] = Field(
        default=None, foreign_key="author.id", primary_key=True
    )


class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    isbn: str

    authors: List["Author"] = Relationship(
        back_populates="books",
        link_model=BookAuthorLink
    )


class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    books: List[Book] = Relationship(
        back_populates="authors",
        link_model=BookAuthorLink
    )
```

### Usage

```python
# Create with relationships
author1 = Author(name="Author One")
author2 = Author(name="Author Two")
book = Book(title="Great Book", isbn="123", authors=[author1, author2])

session.add(book)
session.commit()

# Query
book = session.get(Book, 1)
for author in book.authors:
    print(author.name)

author = session.get(Author, 1)
for book in author.books:
    print(book.title)
```

## One-to-One Relationship

Each side has exactly one related object.

```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str

    profile: Optional["Profile"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False}
    )


class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bio: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", unique=True)

    user: Optional[User] = Relationship(back_populates="profile")
```

## Self-Referential Relationship

A model relating to itself (e.g., Employee and Manager).

```python
class Employee(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    manager_id: Optional[int] = Field(default=None, foreign_key="employee.id")

    # Manager (one)
    manager: Optional["Employee"] = Relationship(
        back_populates="reports",
        sa_relationship_kwargs={"remote_side": "Employee.id"}
    )

    # Direct reports (many)
    reports: List["Employee"] = Relationship(back_populates="manager")
```

## Eager Loading (Avoiding N+1)

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload, joinedload

# selectinload - separate query for related objects (better for large sets)
statement = select(Team).options(selectinload(Team.members))
teams = session.exec(statement).all()

# joinedload - single query with JOIN (better for small sets)
statement = select(Team).options(joinedload(Team.members))
teams = session.exec(statement).all()

# Nested eager loading
statement = select(Team).options(
    selectinload(Team.members).selectinload(Member.tasks)
)
```

## Cascade Delete

```python
from sqlmodel import Relationship

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    members: List["Member"] = Relationship(
        back_populates="team",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

With `cascade="all, delete-orphan"`:
- Deleting a Team automatically deletes all its Members
- Removing a Member from team.members deletes the Member

## Best Practices

1. **Define link tables first** - For many-to-many relationships
2. **Use `back_populates`** - Ensures bidirectional sync
3. **Use `Optional` for nullable FKs** - `team_id: Optional[int]`
4. **Eager load when needed** - Use `selectinload()` to avoid N+1
5. **Consider cascade behavior** - Delete orphans when appropriate
