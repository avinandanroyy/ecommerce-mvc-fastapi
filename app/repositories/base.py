class Repository:
    def __init__(self, db):
        self.db = db

    def get(self, model, id):
        return self.db.query(model).filter(model.id == id).first()

    def get_all(self, model, skip=0, limit=100):
        return self.db.query(model).offset(skip).limit(limit).all()

    def create(self, model, **kwargs):
        obj = model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, model, id, **kwargs):
        obj = self.get(model, id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            self.db.commit()
            self.db.refresh(obj)
        return obj

    def delete(self, model, id):
        obj = self.get(model, id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    def exists(self, model, **kwargs):
        return self.db.query(model).filter_by(**kwargs).first() is not None

    def count(self, model):
        return self.db.query(model).count()
