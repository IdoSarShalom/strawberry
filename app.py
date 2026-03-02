import strawberry

@strawberry.type
class User:
    id: int
    name: str
    age: int

# In-memory database
users_db = [
    User(id=1, name="Alice", age=28),
    User(id=2, name="Bob", age=32)
]

@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> list[User]:
        return users_db

    @strawberry.field
    def user(self, id: int) -> User | None:
        for user in users_db:
            if user.id == id:
                return user
        return None

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_user(self, name: str, age: int) -> User:
        new_id = max((u.id for u in users_db), default=0) + 1
        new_user = User(id=new_id, name=name, age=age)
        users_db.append(new_user)
        return new_user

schema = strawberry.Schema(query=Query, mutation=Mutation)
