from hmac import compare_digest
from sqlalchemy import Column, String, Integer,DateTime
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from typing import Union

# Base = declarative_base()
from model.base import Base


class User(Base):
    __tablename__ = 'User'
   
    id = Column("pk_user",Integer, primary_key=True)
    user_email = Column(String(100),unique=True,nullable=False)
    user_login = Column(String(20),unique=True,nullable=False)
    user_password = Column(String(10),nullable=False)
    user_activation_key = Column(String(20),nullable=True)
    datetime_activation_key = Column(DateTime, nullable=True)
   
    def __init__(self, user_login:str,user_password:str,user_email:str,
                 user_activation_key:str,datetime_activation_key:Union[DateTime, None] = None):
        """
        Cria um tipo de imovel

        Arguments:
            descricao: descricao do tipo de imovel
            data_insercao: data de quando o tipo de imovel foi inserido à base
        """
        self.user_email = user_email
        self.user_login = user_login
        self.user_password = user_password
        self.user_activation_key = user_activation_key
        self.datetime_activation_key = datetime_activation_key
   
    # def check_password(self, user_password):
    #     return compare_digest(user_password, "password")

        