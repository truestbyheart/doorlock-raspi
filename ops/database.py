#!/usr/bin/env python3

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Table,
    Enum,
    ForeignKey,
    MetaData,
    Date,
    inspect,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import text
import enum

Base = declarative_base()
meta = MetaData()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True)
    rf_id = Column(Integer, primary_key=True)
    create_at = Column(Date)
    updated_at = Column(Date)
    logs = relationship("Log", cascade="all, delete")


class CurrentState(enum.Enum):
    IN = "IN"
    OUT = "OUT"


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, autoincrement=True, primary_key=True)
    rf_id = Column(Integer, ForeignKey("users.rf_id"))
    current_state = Column(Enum(CurrentState))
    create_at = Column(Date)
    updated_at = Column(Date)


class Database:
    # DEFINE THE DATABASE CREDENTIALS
    user = ""
    password = ""
    host = ""
    port = 3306
    database = ""
    engine = None

    def __init__(self, user, password, port, host, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def create_connection(self):
        print("postgresql://{0}:{1}@{2}:{3}/{4}".format(
                self.user, self.password, self.host, self.port, self.database
            ))
        return create_engine(
            url="postgresql://{0}:{1}@{2}:{3}/{4}".format(
                self.user, self.password, self.host, self.port, self.database
            )
        )

    def generate_table(self, engine):
        engine.execute(
            text(
                """
                  CREATE TYPE card_state AS ENUM('IN','OUT')
                """
            )
        )
        engine.execute(
            text(
                """
                CREATE TABLE access_logs (
                    id BIGSERIAL NOT NULL,
                    rf_id varchar(255) NOT NULL,
                    current_state card_state DEFAULT NULL,
                    created_at timestamp with time zone DEFAULT now(),
                    updated_at timestamp with time zone DEFAULT now(),
                    PRIMARY KEY (id),
                    FOREIGN KEY (rf_id) REFERENCES users (rf_id) 
                    ON DELETE CASCADE ON UPDATE CASCADE
                )
            """
            )
        )

        engine.execute(
            text(
                """
                  CREATE TABLE users (
                        id BIGSERIAL NOT NULL,
                        full_name varchar(255) NOT NULL,
                        rf_id varchar(255) PRIMARY KEY NOT NULL,
                        created_at timestamp with time zone DEFAULT now(),
                        updated_at timestamp with time zone DEFAULT now()
                    )
                """
            )
        )
        
    def query_runner(self, query):
        try:
            print(f"Query Executing: {query}")
            return self.engine.execute(text(query)).all()
        except Exception as ex:
            print(f"{query} failed because of: {ex}")
            
    def add_log_entry(self, rf_id, state):
        return self.query_runner(f"""INSERT INTO access_logs(rf_id, current_state) VALUES ("{rf_id}", "{state}")""")        
            
    def check_if_user_exists(self, rf_id):
        return self.query_runner(f"""SELECT * FROM users WHERE rf_id="{rf_id}" """) 
        
    def get_last_log_entry(self, rf_id):
        return self.query_runner(f"""SELECT * FROM access_logs WHERE rf_id="{rf_id}" ORDER BY id  DESC LIMIT 1""")            

    def get_connection(self):
        try:
            # TABLES
            # GET THE CONNECTION OBJECT (ENGINE) FOR THE DATABASE
            engine = self.create_connection()
            self.generate_table(engine)
            self.engine = engine
            print(
                f"Connection to the {self.host} for user {self.user} created successfully."
            )
            return engine
        except Exception as ex:
            print("Connection could not be made due to the following error: \n", ex)
