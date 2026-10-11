from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Create SQLAlchemy Database Engine for PostgreSQL
# Automatically ensure psycopg2 dialect is used if postgresql:// prefix is provided
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    echo=False
)

# Create SessionLocal class for DB session instantiation
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base for models
Base = declarative_base()

# Dependency to get DB session in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Tests the PostgreSQL connection using the configured engine."""
    from sqlalchemy import text
    with engine.connect() as conn:
        return conn.execute(text("SELECT 1")).scalar()

def create_tables():
    """Creates all defined database tables in PostgreSQL via SQLAlchemy metadata."""
    import app.models  # Ensures all ORM models are registered with Base.metadata
    Base.metadata.create_all(bind=engine)

