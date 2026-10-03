import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base
from app.models.models import *
from app.data.synthetic_generator import seed_database

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    
    # Seed initial test data
    seed_database(session, force_reset=False)
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)
