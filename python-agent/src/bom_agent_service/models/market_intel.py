"""Models for market intelligence data."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class IntelCategory(str, Enum):
    """Category of market intelligence."""
    SUPPLY_CHAIN = "supply_chain"
    MANUFACTURER_NEWS = "manufacturer_news"
    COMPONENT_SHORTAGE = "component_shortage"
    PRICE_TREND = "price_trend"
    LIFECYCLE = "lifecycle"
    REGULATORY = "regulatory"
    GENERAL = "general"


class IntelSentiment(str, Enum):
    """Sentiment of the intelligence."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class MarketIntelItem(BaseModel):
    """A single piece of market intelligence."""
    intel_id: str = Field(description="Unique identifier for this intel item")
    source_url: str = Field(description="URL where this intel was found")
    title: str = Field(description="Title or headline")
    summary: str = Field(description="Brief summary of the intel")
    full_text: str = Field(default="", description="Full text content")
    category: IntelCategory = Field(default=IntelCategory.GENERAL)
    sentiment: IntelSentiment = Field(default=IntelSentiment.NEUTRAL)
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Relevance score 0-1")
    related_mpns: list[str] = Field(default_factory=list, description="MPNs this intel relates to")
    related_manufacturers: list[str] = Field(default_factory=list, description="Manufacturers mentioned")
    keywords: list[str] = Field(default_factory=list, description="Keywords extracted")
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None, description="When this intel expires")


class MarketIntelReport(BaseModel):
    """Aggregated market intelligence report for a set of parts."""
    report_id: str
    project_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # Aggregated intel items
    items: list[MarketIntelItem] = Field(default_factory=list)

    # Summary statistics
    total_sources_scraped: int = 0
    total_items_found: int = 0

    # Key findings (populated by MarketIntelAgent)
    supply_chain_risks: list[str] = Field(default_factory=list, description="Identified supply chain risks")
    shortage_alerts: list[str] = Field(default_factory=list, description="Parts with shortage warnings")
    price_trends: dict[str, str] = Field(default_factory=dict, description="MPN to price trend (up/down/stable)")
    manufacturer_updates: list[str] = Field(default_factory=list, description="Notable manufacturer news")
    recommendations: list[str] = Field(default_factory=list, description="Recommended actions")

    def get_intel_for_mpn(self, mpn: str) -> list[MarketIntelItem]:
        """Get all intel items related to a specific MPN."""
        return [item for item in self.items if mpn.upper() in [m.upper() for m in item.related_mpns]]

    def get_intel_for_manufacturer(self, manufacturer: str) -> list[MarketIntelItem]:
        """Get all intel items related to a specific manufacturer."""
        mfg_lower = manufacturer.lower()
        return [
            item for item in self.items
            if any(mfg_lower in m.lower() for m in item.related_manufacturers)
        ]

    def get_high_relevance_items(self, threshold: float = 0.7) -> list[MarketIntelItem]:
        """Get items with relevance score above threshold."""
        return [item for item in self.items if item.relevance_score >= threshold]

    def get_negative_sentiment_items(self) -> list[MarketIntelItem]:
        """Get items with negative sentiment (potential risks)."""
        return [item for item in self.items if item.sentiment == IntelSentiment.NEGATIVE]
