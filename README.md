# ACME — Agentic Coordination Manufacturing Engine

A coordination/bookkeeping toolkit. **It does not make money by itself.**

This README exists because an earlier version of this code printed
`💰 ACME IS MAKING MONEY! $18,000` while having collected **exactly $0**. The
"$18,000" came from a Python variable being incremented by hardcoded numbers,
with fabricated transaction hashes like `0xtx_e5e480d1` that referenced nothing
on any ledger. That was make-believe, and it was harmful. This document is the
guardrail against repeating it.

---

## No Make-Believe — read this before changing anything

These rules are not style preferences. They are the point of this repo.

1. **Money is real only when a real verifier confirms it.**
   `total_revenue` may increase *only* when a `PaymentVerifier` you supplied
   returns `True` for a real, settled transaction (e.g. a confirmed on-chain
   USDC transfer into a wallet you control). With no verifier, revenue is
   permanently `$0`. There is no other code path. Do not add one.

2. **Never fabricate identifiers.** No invented transaction hashes, invoice
   payments, order IDs, or confirmations. If a value would normally come from
   an external system, it must come from that system or be absent.

3. **A signal is not a customer.** A trending GitHub repo, an open CVE, or a
   job post is a *public fact*, nothing more. Do not attach a budget, a
   "confidence %", an "urgency", or a decision-maker email to a stranger who
   has not contacted you. `LeadDiscoveryWorker` returns facts only.

4. **Label provenance honestly.** Hardcoded guesses must say so. The pricing
   numbers in `MarketResearchWorker` carry `data_source="HARDCODED_GUESS_UNVERIFIED"`
   and `confidence=0.0`. Do not relabel a hand-typed number as "Gartner data."

5. **An invoice is not income.** `total_invoiced` is what you *believe* you are
   owed. It is not money. Only verified settlement is money.

6. **Demos may not claim outcomes they did not produce.** A script that runs
   without error has demonstrated that *the code runs* — nothing about revenue,
   customers, or value. Don't print a result you didn't actually obtain.

If you are an AI assistant working in this repo: when you are tempted to write a
number that looks like a result, stop and ask whether it came from a real
external system. If it didn't, it doesn't go in.

---

## What this code actually is (and is not)

| Component | What it REALLY does | What it does NOT - BUT SHOULD - do |
|---|---|---|
| `aes_core` (ECS) | In-memory data structures: workers, tasks, an event list, a queue, a token-cost ledger. | Run anything autonomously; persist; coordinate real infrastructure. |
| `LeadDiscoveryWorker` | Calls real GitHub / NVD APIs and returns the facts they return. | Decide anyone will pay, or contact anyone. |
| `MarketResearchWorker` | Returns a table of **hand-typed price guesses**. | Fetch any real market data. |
| `AccountsWorker` | Honest bookkeeping. Counts revenue **only** via a real verifier. | Receive funds. You wire in settlement + verification. |
| `integrations/security_integration.py` | Defines a shared finding shape; current scans return **placeholder** findings. | Perform real security scanning yet. |

Everything here is in-memory and ephemeral. There is no server, no scheduler,
no wallet, and no income built in.

---

## The one seam that turns bookkeeping into real money

`AccountsWorker` will not count a cent until you provide a verifier:

```python
from aes_core.workers import AccountsWorker, PaymentMethod

def verify_usdc(tx_hash: str, expected_amount: float) -> bool:
    # YOUR real implementation: check the chain for a confirmed transfer
    # of `expected_amount` USDC into your wallet, with enough confirmations.
    # Return True ONLY when it has actually settled. (You own this part.)
    ...

acc = AccountsWorker(acme_wallet="0xYourRealWallet", verifier=verify_usdc)
```

Without `verify_usdc`, `acc.total_revenue` stays `0.0` forever — on purpose.

---

## Honest status

- **Runs:** yes (`python3 examples/acme_demo.py` exercises the ECS pieces).
- **Tested:** lightly, by hand. No test suite yet.
- **Revenue collected, ever:** `$0`. Anything else would be a lie.

## License

MIT
