"""
Lead Discovery Worker: surface REAL public signals. Invent nothing.

HARD RULES (see README "No Make-Believe"):
- This module returns only facts returned by an API.
- It does NOT assign a budget, a "confidence", an "urgency", or a
  decision-maker email to anyone. Nobody has asked you for anything.
  A trending repo is not a customer. A CVE is not a contract.
- A "lead" here means: a real, public, verifiable URL you could choose
  to contact. Nothing about money is implied or promised.
"""

import os
import requests
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone


@dataclass
class Lead:
    """A real, public signal. Facts only — no invented sales data."""

    source: str            # which API this came from
    entity: str            # repo owner / org name as returned by the API
    url: str               # public URL a human can open and verify
    signal: str            # the literal fact observed (e.g. "4200 stars")
    raw: Dict[str, Any] = field(default_factory=dict)  # untouched API payload
    observed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class LeadDiscoveryWorker:
    """
    Pulls public signals from real APIs. Returns facts.

    What it CANNOT do (and won't fake): decide someone will pay, how much,
    or that they want a service. That is sales, done by a human, with a
    real conversation and a real yes.
    """

    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.leads: List[Lead] = []
        self.errors: List[str] = []

    def from_github(self, query: str, limit: int = 5) -> List[Lead]:
        """Return real repos matching a query. No budgets, no emails invented."""
        leads: List[Lead] = []
        headers = {"Accept": "application/vnd.github+json"}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        try:
            resp = requests.get(
                "https://api.github.com/search/repositories",
                params={"q": query, "sort": "stars", "order": "desc", "per_page": limit},
                headers=headers,
                timeout=10,
            )
            resp.raise_for_status()
            for repo in resp.json().get("items", []):
                leads.append(
                    Lead(
                        source="github_search",
                        entity=repo["owner"]["login"],
                        url=repo["html_url"],
                        signal=f"{repo['stargazers_count']} stars; query={query!r}",
                        raw={
                            "full_name": repo["full_name"],
                            "stars": repo["stargazers_count"],
                            "language": repo.get("language"),
                            "open_issues": repo.get("open_issues_count"),
                        },
                    )
                )
        except requests.RequestException as e:
            self.errors.append(f"github: {e}")
        self.leads.extend(leads)
        return leads

    def from_nvd_cves(self, limit: int = 5) -> List[Lead]:
        """Return real recently-published CVEs. A CVE is a fact, not a client."""
        leads: List[Lead] = []
        try:
            resp = requests.get(
                "https://services.nvd.nist.gov/rest/json/cves/2.0",
                params={"resultsPerPage": limit, "startIndex": 0},
                timeout=15,
            )
            resp.raise_for_status()
            for item in resp.json().get("vulnerabilities", []):
                cve = item.get("cve", {})
                cve_id = cve.get("id", "UNKNOWN")
                desc = ""
                for d in cve.get("descriptions", []):
                    if d.get("lang") == "en":
                        desc = d.get("value", "")
                        break
                leads.append(
                    Lead(
                        source="nvd_cve",
                        entity=cve_id,
                        url=f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                        signal=desc[:160],
                        raw={"cve_id": cve_id},
                    )
                )
        except requests.RequestException as e:
            self.errors.append(f"nvd: {e}")
        self.leads.extend(leads)
        return leads

    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run real lookups. Returns facts + any errors. No revenue projection,
        because none exists until a human closes a deal.
        """
        found: List[Lead] = []
        gh_query = parameters.get("github_query")
        if gh_query:
            found.extend(self.from_github(gh_query, parameters.get("limit", 5)))
        if parameters.get("nvd"):
            found.extend(self.from_nvd_cves(parameters.get("limit", 5)))

        return {
            "leads_found": len(found),
            "leads": [
                {"source": l.source, "entity": l.entity, "url": l.url, "signal": l.signal}
                for l in found
            ],
            "errors": self.errors,
            "note": "These are public signals only. None of these parties have "
                    "agreed to pay anything. Contacting them is a human decision.",
        }
