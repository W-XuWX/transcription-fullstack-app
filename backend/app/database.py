from sqlalchemy import create_engine, URL, exc
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

class DBClient:

    def __init__(self, config):
        sqlite_url = URL.create(
            drivername=config.db_drivername,
            database=config.db_database
        )
        try:
            engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
            
            self.session = sessionmaker(
                autocommit=False,
                autoflush=True,
                bind=engine)()
        except exc.SQLAlchemyError as e:
            logger.error(f"Error: Failed to create database engine - {e}")
            raise

    def __del__(self):
        """
        Destructor to ensure resources are cleaned up when the object is destroyed
        """
        self.deinit()

    def deinit(self):
        """
        Cleans up resources by closing the session.
        """
        if self.session:
            logger.info("Closing session")
            self.session.close()