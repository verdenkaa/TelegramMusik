import sqlalchemy
from .db_session import SqlAlchemyBase


class Song(SqlAlchemyBase):
    __tablename__ = 'songs'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    qr = sqlalchemy.Column(sqlalchemy.String)
    song = sqlalchemy.Column(sqlalchemy.String)
    text = sqlalchemy.Column(sqlalchemy.String, index=True)
    image = sqlalchemy.Column(sqlalchemy.String)