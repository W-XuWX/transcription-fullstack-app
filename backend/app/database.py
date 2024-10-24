from sqlalchemy import create_engine, URL, exc, text
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
            self.engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
            
            self.session = sessionmaker(
                autocommit=False,
                autoflush=True,
                bind=self.engine)()
            
        except exc.SQLAlchemyError as e:
            logger.error(f"Error: Failed to create database engine - {e}")
            raise

    def init_fts(self):
        """Initialize FTS tables and triggers"""
        try:
            # Create FTS virtual table if it doesn't exist
            self.session.execute(text("""
                CREATE VIRTUAL TABLE IF NOT EXISTS results_search USING fts5(
                    id,
                    file_name,
                    transcription,
                    content=results,
                    content_rowid=id
                )
            """))

            # Drop existing triggers one by one
            self.session.execute(text("DROP TRIGGER IF EXISTS results_ai"))
            self.session.execute(text("DROP TRIGGER IF EXISTS results_ad"))
            self.session.execute(text("DROP TRIGGER IF EXISTS results_au"))

            # After INSERT trigger
            self.session.execute(text("""
                CREATE TRIGGER results_ai AFTER INSERT ON results BEGIN
                    INSERT INTO results_search(id, file_name, transcription)
                    VALUES (new.id, new.file_name, new.transcription);
                END;
            """))

            # After DELETE trigger
            self.session.execute(text("""
                CREATE TRIGGER results_ad AFTER DELETE ON results BEGIN
                    DELETE FROM results_search WHERE id = old.id;
                END;
            """))

            # After UPDATE trigger
            self.session.execute(text("""
                CREATE TRIGGER results_au AFTER UPDATE ON results BEGIN
                    UPDATE results_search 
                    SET file_name = new.file_name,
                        transcription = new.transcription
                    WHERE id = old.id;
                END;
            """))

            # Populate FTS table with existing data
            self.session.execute(text("""
                INSERT OR IGNORE INTO results_search(id, file_name, transcription)
                SELECT id, file_name, transcription FROM results
                WHERE id NOT IN (SELECT id FROM results_search);
            """))

            self.session.commit()
            logger.info("FTS tables and triggers initialized successfully")
        except exc.SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error initializing FTS: {e}")
            raise

    def __del__(self):
        self.deinit()

    def deinit(self):
        if hasattr(self, 'session') and self.session:
            try:
                logger.info("Closing database session")
                self.session.close()
            except Exception as e:
                logger.error(f"Error closing database session: {e}")