import threading
from sqlalchemy import create_engine
from sqlalchemy import Column, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.pool import StaticPool
from mfinder import DB_URL


BASE = declarative_base()


class BanList(BASE):
    __tablename__ = "banlist"
    user_id = Column(Numeric, primary_key=True)


    def __init__(self, user_id):
        self.user_id = user_id



def start() -> scoped_session:
    engine = create_engine(DB_URL, client_encoding="utf8", poolclass=StaticPool)
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


SESSION = start()
INSERTION_LOCK = threading.RLock()


async def ban_user(user_id):
    with INSERTION_LOCK:
        try:
            usr = SESSION.query(BanList).filter_by(user_id=user_id).one()
        except NoResultFound:
            usr = BanList(user_id=user_id)
            SESSION.add(usr)
            SESSION.commit()
            return True


async def is_banned(user_id):
    with INSERTION_LOCK:
        try:
            usr = SESSION.query(BanList).filter_by(user_id=user_id).one()
            return usr.user_id
        except NoResultFound:
            return False


async def unban_user(user_id):
    with INSERTION_LOCK:
        try:
            usr = SESSION.query(BanList).filter_by(user_id=user_id).one()
            SESSION.delete(usr)
            SESSION.commit()
            return True
        except NoResultFound:
            return False
