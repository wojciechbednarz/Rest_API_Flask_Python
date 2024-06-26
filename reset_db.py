from models.user import UserModel
from models.tag import TagModel
from models.store import StoreModel
from models.item import ItemModel
from db import db


def reset_db():
    db.session.query(UserModel).delete()
    db.session.query(TagModel).delete()
    db.session.query(StoreModel).delete()
    db.session.query(ItemModel).delete()
    db.session.commit()
