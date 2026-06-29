"""
Pricing Estimate Worker: HARDCODED ballpark ranges. NOT fetched data.

HONESTY NOTE (see README "No Make-Believe"):
- Every number in this file is a hand-typed guess based on general
  knowledge of the market. NONE of it is fetched from Gartner, SANS,
  Glassdoor, or any API. Do not present these as researched figures.
- They are starting points for a human to sanity-check, not facts.
- If you want real numbers, wire up a real source and DELETE these.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

# Single source of truth for the provenance of every number below.
PROVENANCE = "HARDCODED_GUESS_UNVERIFIED"


class ServiceType(str, Enum):
    SECURITY_AUDIT = "security_audit"
    PENETRATION_TEST = "penetration_testing"
    CODE_REVIEW = "code_review"
    DEPLOYMENT = "deployment"
    CONSULTING = "consulting"


@dataclass
class MarketData:
    """A hand-typed pricing guess. Not researched. Not authoritative."""

    service_type: ServiceType
    market_rate_low: float
    market_rate_high: float
    market_rate_avg: float
    demand_level: str  # subjective guess
    willingness_to_pay_by_size: Dict[str, float]
    recommended_price: float
    confidence: float  # how much YOU should trust this: treat as low
    data_source: str = PROVENANCE


class MarketResearchWorker:
    """
    Holds hand-typed pricing guesses. Does not call any API.

    Honest naming: this is not "research". It is a lookup table of guesses
    a human typed. Use it to start a conversation, never to quote a client.
    """

    def __init__(self):
        self.market_data: Dict[ServiceType, MarketData] = {}
        self._load_hardcoded_guesses()

    def _load_hardcoded_guesses(self) -> None:
        """Load hand-typed estimates. NOTHING here is fetched."""

        # All numbers below are hand-typed guesses. confidence is deliberately
        # low to signal "verify before you ever quote this to anyone".
        self.market_data[ServiceType.SECURITY_AUDIT] = MarketData(
            service_type=ServiceType.SECURITY_AUDIT,
            market_rate_low=2500,
            market_rate_high=25000,
            market_rate_avg=8000,
            demand_level="unknown",
            willingness_to_pay_by_size={
                "startup": 2500, "scaleup": 6000, "mid_market": 12000, "enterprise": 25000,
            },
            recommended_price=8000,
            confidence=0.0,
        )
        self.market_data[ServiceType.PENETRATION_TEST] = MarketData(
            service_type=ServiceType.PENETRATION_TEST,
            market_rate_low=5000,
            market_rate_high=75000,
            market_rate_avg=22000,
            demand_level="unknown",
            willingness_to_pay_by_size={
                "startup": 5000, "scaleup": 18000, "mid_market": 40000, "enterprise": 75000,
            },
            recommended_price=22000,
            confidence=0.0,
        )
        self.market_data[ServiceType.CODE_REVIEW] = MarketData(
            service_type=ServiceType.CODE_REVIEW,
            market_rate_low=1200,
            market_rate_high=8000,
            market_rate_avg=3500,
            demand_level="unknown",
            willingness_to_pay_by_size={
                "startup": 1200, "scaleup": 2500, "mid_market": 5000, "enterprise": 8000,
            },
            recommended_price=3500,
            confidence=0.0,
        )
        self.market_data[ServiceType.DEPLOYMENT] = MarketData(
            service_type=ServiceType.DEPLOYMENT,
            market_rate_low=3500,
            market_rate_high=30000,
            market_rate_avg=10000,
            demand_level="unknown",
            willingness_to_pay_by_size={
                "startup": 3500, "scaleup": 8000, "mid_market": 15000, "enterprise": 30000,
            },
            recommended_price=10000,
            confidence=0.0,
        )
        self.market_data[ServiceType.CONSULTING] = MarketData(
            service_type=ServiceType.CONSULTING,
            market_rate_low=180,
            market_rate_high=500,
            market_rate_avg=350,
            demand_level="unknown",
            willingness_to_pay_by_size={
                "startup": 180, "scaleup": 280, "mid_market": 400, "enterprise": 500,
            },
            recommended_price=350,
            confidence=0.0,
        )

    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute market research for a service."""
        service_type_str = parameters.get("service_type", "security_audit")
        company_size = parameters.get("company_size", "mid_market")

        try:
            service_type = ServiceType(service_type_str)
            market_data = self.market_data.get(service_type)

            if not market_data:
                return {"error": f"No market data for {service_type_str}"}

            price = market_data.willingness_to_pay_by_size.get(company_size, market_data.recommended_price)

            return {
                "service": service_type_str,
                "company_size": company_size,
                "estimate_range": f"${market_data.market_rate_low:,.0f} - ${market_data.market_rate_high:,.0f}",
                "midpoint_guess": market_data.market_rate_avg,
                "suggested_starting_point": price,
                "demand": market_data.demand_level,
                "confidence": market_data.confidence,
                "data_source": market_data.data_source,  # == HARDCODED_GUESS_UNVERIFIED
                "warning": "Hand-typed guess. Verify against a real quote before using.",
                "status": "complete",
            }
        except ValueError:
            return {"error": f"Unknown service type: {service_type_str}"}

    def get_all_pricing(self) -> Dict[str, Dict[str, Any]]:
        """Get all market pricing data."""
        return {
            service.value: {
                "low": data.market_rate_low,
                "avg": data.market_rate_avg,
                "high": data.market_rate_high,
                "recommended": data.recommended_price,
                "demand": data.demand_level,
                "source": data.data_source,
            }
            for service, data in self.market_data.items()
        }
