import sqlite3

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.connection = sqlite3.connect("db.sqlite3")
            cls._instance.connection.row_factory = sqlite3.Row
            cls._instance.cursor = cls._instance.connection.cursor()
        return cls._instance

    def execute(self, sql, params=()):
        sql_print = sql.replace('\n', ' ')
        print(f"SQL: {sql_print}")
        if params:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        self.connection.commit()
        return self.cursor

class Field:
    def __init__(self, primary_key=False, nullable=False, unique=False):
        self.primary_key = primary_key
        self.nullable = nullable
        self.unique = unique

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def get_sql_type(self):
        raise NotImplementedError

    def get_sql_definition(self):
        def_parts = [self.name, self.get_sql_type()]
        if self.primary_key:
            def_parts.append("PRIMARY KEY AUTOINCREMENT")
        if not self.nullable and not self.primary_key:
            def_parts.append("NOT NULL")
        if self.unique:
            def_parts.append("UNIQUE")
        return " ".join(def_parts)

class CharField(Field):
    def __init__(self, max_length=255, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length

    def get_sql_type(self):
        return f"VARCHAR({self.max_length})"

class IntegerField(Field):
    def get_sql_type(self):
        return "INTEGER"
        
class ReverseRelation:
    def __init__(self, related_model, related_field_name):
        self.related_model = related_model
        self.related_field_name = related_field_name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        rel_model = Model._decl_registry.get(self.related_model) if isinstance(self.related_model, str) else self.related_model
        return rel_model.filter(**{self.related_field_name: instance.id}).all()

class ForeignKey(Field):
    def __init__(self, to, related_name=None, **kwargs):
        super().__init__(**kwargs)
        self.to = to
        self.related_name = related_name

    def __set_name__(self, owner, name):
        self.name = f"{name}_id"
        self.virtual_name = name
        
    def __get__(self, instance, owner):
        if instance is None:
            return self
        foreign_id = instance.__dict__.get(self.name)
        if foreign_id is None:
            return None
        to_model = Model._decl_registry.get(self.to) if isinstance(self.to, str) else self.to
        results = to_model.filter(id=foreign_id).all()
        return results[0] if results else None

    def __set__(self, instance, value):
        to_model = Model._decl_registry.get(self.to) if isinstance(self.to, str) else self.to
        if to_model and isinstance(value, to_model):
            instance.__dict__[self.name] = value.id
            instance.__dict__[self.virtual_name] = value
        else:
            instance.__dict__[self.name] = value

    def get_sql_type(self):
        return "INTEGER"

class QuerySet:
    def __init__(self, model_class):
        self.model_class = model_class
        self.filters = {}
        self.order_by_field = None
        self.db = Database()

    def filter(self, **kwargs):
        for k, v in kwargs.items():
            self.filters[k] = v
        return self

    def order_by(self, field):
        self.order_by_field = field
        return self

    def all(self):
        table_name = self.model_class.__tablename__
        query = f"SELECT * FROM {table_name}"
        params = []
        if self.filters:
            conditions = []
            for k, v in self.filters.items():
                if k.endswith("__gte"):
                    col = k[:-5]
                    conditions.append(f"{col} >= ?")
                else:
                    col = k
                    conditions.append(f"{col} = ?")
                params.append(v)
            query += " WHERE " + " AND ".join(conditions)
        if self.order_by_field:
            if self.order_by_field.startswith("-"):
                query += f" ORDER BY {self.order_by_field[1:]} DESC"
            else:
                query += f" ORDER BY {self.order_by_field} ASC"

        cursor = self.db.execute(query, tuple(params))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            obj = self.model_class(**dict(row))
            results.append(obj)
        return results

class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        if name == "Model":
            return super().__new__(mcs, name, bases, attrs)

        fields = {"id": IntegerField(primary_key=True)}
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                if getattr(value, 'name', None) is None:
                    # Manually set name if __set_name__ hasn't been called yet.
                    if isinstance(value, ForeignKey):
                        value.name = f"{key}_id"
                        value.virtual_name = key
                    else:
                        value.name = key
                fields[value.name] = value

        attrs["_fields"] = fields
        attrs["__tablename__"] = name.lower()
        
        cls = super().__new__(mcs, name, bases, attrs)
        return cls

class Model(metaclass=ModelMeta):
    _decl_registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, '_decl_registry') or cls._decl_registry is Model._decl_registry:
             # Ensure the dictionary is bound on the base Model correctly or handle globally
             pass
        Model._decl_registry[cls.__name__] = cls

        for key, field in cls._fields.items():
            if isinstance(field, ForeignKey) and getattr(field, 'related_name', None):
                to_model_name = field.to if isinstance(field.to, str) else field.to.__name__
                # Defer adding reverse relation since target model might not be registered yet.
                # Actually, wait, it's safer to register reverse relations globally.
                to_model = Model._decl_registry.get(to_model_name)
                if to_model:
                     setattr(to_model, field.related_name, ReverseRelation(cls.__name__, field.name))
                     
    @classmethod
    def create_table(cls):
        db = Database()
        field_defs = []
        for field_name, field in cls._fields.items():
            # Adjusting name to ensure it correctly picks up the name
            if not hasattr(field, 'name'):
                field.name = field_name
            field_defs.append(field.get_sql_definition())
        
        query = f"CREATE TABLE IF NOT EXISTS {cls.__tablename__} (\n    "
        query += ",\n    ".join(field_defs)
        query += "\n);"
        
        print("SQL:", query.replace('\n', ' '))
        db.execute(query)
        print(f"Table '{cls.__tablename__}' created.")

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def filter(cls, **kwargs):
        return QuerySet(cls).filter(**kwargs)

    def save(self):
        db = Database()
        fields = []
        values = []
        placeholders = []
        for key, field in self._fields.items():
            if key == "id" and getattr(self, "id", None) is None:
                continue
            val = getattr(self, key)
            if val is not None:
                fields.append(key)
                values.append(val)
                placeholders.append("?")

        fields_str = ", ".join(fields)
        placeholders_str = ", ".join(placeholders)
        
        query = f"INSERT INTO {self.__tablename__} ({fields_str}) VALUES ({placeholders_str});"
        cursor = db.execute(query, tuple(values))
        self.id = cursor.lastrowid
        print(f"SQL: {query}")
        print(f"Record saved: {self}")

    def delete(self):
         db = Database()
         if getattr(self, "id", None):
             query = f"DELETE FROM {self.__tablename__} WHERE id = ?"
             db.execute(query, (self.id,))
             print(f"Record deleted: {self}")

    def __repr__(self):
        attrs = []
        for key in self._fields.keys():
            val = self.__dict__.get(key)
            if val is not None:
                attrs.append(f"{key}={repr(val)}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"

# --- Setup Deferred Relations ---
def setup_deferred_relations():
    for model_name, model_cls in Model._decl_registry.items():
        for field in model_cls._fields.values():
            if isinstance(field, ForeignKey) and field.related_name:
                to_model_name = field.to if isinstance(field.to, str) else field.to.__name__
                to_model = Model._decl_registry.get(to_model_name)
                if to_model:
                     setattr(to_model, field.related_name, ReverseRelation(model_cls.__name__, field.name))

# Decorator pattern (class decorator)
def register_model(cls):
    Model._decl_registry[cls.__name__] = cls
    setup_deferred_relations()
    return cls

# --- Developer Usage ---
if __name__ == "__main__":
    import os
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")

    @register_model
    class User(Model):
        name = CharField(max_length=100)
        email = CharField(max_length=255, unique=True)
        age = IntegerField(nullable=True)

    @register_model
    class Post(Model):
        title = CharField(max_length=200)
        author = ForeignKey(User, related_name="posts")
        
    setup_deferred_relations()

    # --- Runtime Output ---
    User.create_table()
    Post.create_table()
    
    alice = User(name="Alice", email="alice@example.com", age=30)
    alice.save()
    
    post1 = Post(title="Hello World", author_id=alice.id)
    post1.save()

    users = User.filter(age__gte=25).order_by("-name").all()
    print(users)
    
    print(alice.posts)

