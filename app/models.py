# app/models.py
import os
from datetime import datetime
from urllib.parse import urlparse

from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean, DateTime, Text, LargeBinary, Index
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/site_inspector")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def _domain_from_url(u: str | None) -> str | None:
    if not u:
        return None
    try:
        return urlparse(u).netloc or None
    except Exception:
        return None

class Hit404(Base):
    __tablename__ = "hits_404"

    id = BigInteger().with_variant(Integer, "sqlite")  # compat sqlite si besoin
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    ts = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    url = Column(Text, nullable=False)
    referrer = Column(Text)
    referrer_domain = Column(String(255))
    user_agent = Column(Text)
    ip = Column(INET)
    source = Column(String(16), nullable=False)  # 'crawler' | 'nginx' | 'app'

    is_internal = Column(Boolean)
    is_bot = Column(Boolean)
    pattern = Column(String(32))  # 'slash','case','locale','noise','unknown'

    dedup_hash = Column(LargeBinary)  # optionnel, si tu veux dédoublonner

    # Index utiles
    __table_args__ = (
        Index("idx_hits_404_ts", "ts"),
        Index("idx_hits_404_refdom", "referrer_domain"),
        Index("idx_hits_404_source", "source"),
        Index("idx_hits_404_isbot", "is_bot"),
    )

def init_db():
    Base.metadata.create_all(bind=engine)
