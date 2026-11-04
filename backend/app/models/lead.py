from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class HealthcareLead(Base):
    __tablename__ = "healthcare_leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    business_type = Column(String(100), nullable=True, default="Clinic", index=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True, index=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True, default="Global", index=True)
    postal_code = Column(String(50), nullable=True)
    phone = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    website = Column(String(500), nullable=True)
    normalized_website = Column(String(500), nullable=True, index=True)
    services = Column(JSON, nullable=True)  # List of service strings
    source_url = Column(String(1000), nullable=False)
    source_type = Column(String(50), nullable=False, default="WEBSITE")
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="NEW", index=True)
    raw_data = Column(JSON, nullable=True)  # Stores Schema.org or scraped metadata for auditability
    
    # AI Intelligence Fields
    ai_analysis = Column(JSON, nullable=True)  # {business_type, services_summary, target_audience, observations}
    ai_opportunities = Column(JSON, nullable=True)  # [{title, explanation}]
    ai_score = Column(Integer, nullable=True)  # 0 - 100
    ai_score_category = Column(String(50), nullable=True)  # "High" | "Medium" | "Low"
    ai_score_reason = Column(Text, nullable=True)
    ai_outreach_subject = Column(String(255), nullable=True)
    ai_outreach_body = Column(Text, nullable=True)
    ai_analyzed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<HealthcareLead(id={self.id}, name='{self.name}', city='{self.city}')>"
