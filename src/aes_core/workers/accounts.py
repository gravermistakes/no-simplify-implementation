"""
Accounts Worker: bookkeeping for REAL, VERIFIED money only.

THE ONE RULE (see README "No Make-Believe"):
- A payment is counted as revenue IF AND ONLY IF a verifier function
  confirms a real transaction actually settled (e.g. an on-chain USDC
  transfer into your wallet). No verifier => the payment is recorded as
  UNVERIFIED and contributes $0 to revenue.
- There are NO fabricated transaction hashes anywhere in this file.
- Invoices are just bookkeeping (what you BELIEVE you're owed). They are
  not income. Income is only verified settlement.

The verifier is YOUR blockchain layer. Until you pass one in, this module
will honestly refuse to claim any revenue.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid

# A PaymentVerifier takes a tx hash + expected amount and returns True only
# if it confirmed, on a real ledger, that the funds actually settled.
PaymentVerifier = Callable[[str, float], bool]


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    USDC = "usdc"
    ETH = "eth"
    BANK_TRANSFER = "bank_transfer"
    PENDING = "pending"


@dataclass
class Payment:
    """A claimed payment. Only counts as revenue if verified is True."""

    id: str
    amount: float  # USD equivalent
    method: PaymentMethod
    tx_hash: Optional[str] = None   # real ledger reference, or None
    verified: bool = False          # set True ONLY by a real verifier
    received_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Invoice:
    """Customer invoice with real accounting."""

    id: str
    customer_id: str
    amount: float  # USD
    description: str
    line_items: List[Dict[str, Any]] = field(default_factory=list)  # Itemized work
    status: InvoiceStatus = InvoiceStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    due_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    payments: List[Payment] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def paid_amount(self) -> float:
        """Total amount actually paid — VERIFIED payments only."""
        return sum(p.amount for p in self.payments if p.verified)

    def remaining_amount(self) -> float:
        """Amount still owed."""
        return max(0, self.amount - self.paid_amount())

    def is_fully_paid(self) -> bool:
        """Check if invoice is fully paid."""
        return self.remaining_amount() <= 0.01  # Account for floating point

    def is_overdue(self) -> bool:
        """Check if invoice is overdue."""
        return datetime.now() > self.due_date and not self.is_fully_paid()


@dataclass
class CustomerAccount:
    """Real customer account with lifecycle tracking."""

    id: str
    name: str
    email: str
    contract_value: Optional[float] = None  # Total contract value if applicable
    total_invoiced: float = 0.0
    total_paid: float = 0.0
    invoices: List[Invoice] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def invoice_count(self) -> int:
        """Number of invoices created."""
        return len(self.invoices)

    def paid_invoices(self) -> int:
        """Number of fully paid invoices."""
        return sum(1 for inv in self.invoices if inv.is_fully_paid())

    def payment_rate(self) -> float:
        """What percentage of invoiced amount has been paid."""
        if self.total_invoiced == 0:
            return 0.0
        return (self.total_paid / self.total_invoiced) * 100

    def profit(self) -> float:
        """Profit from this customer (revenue - cost)."""
        # Cost tracked separately in ACME economics
        return self.total_paid

    def create_invoice(
        self,
        amount: float,
        description: str,
        line_items: Optional[List[Dict[str, Any]]] = None,
    ) -> Invoice:
        """Create new invoice for customer."""
        invoice = Invoice(
            id=str(uuid.uuid4()),
            customer_id=self.id,
            amount=amount,
            description=description,
            line_items=line_items or [],
        )
        self.invoices.append(invoice)
        self.total_invoiced += amount
        return invoice

    def receive_payment(
        self,
        invoice_id: str,
        amount: float,
        method: PaymentMethod,
        tx_hash: Optional[str],
        verified: bool,
    ) -> Optional[Payment]:
        """
        Attach a payment to an invoice. Only VERIFIED payments move total_paid
        or change invoice status. Unverified claims are kept for audit but
        count as $0.
        """
        for invoice in self.invoices:
            if invoice.id == invoice_id:
                payment = Payment(
                    id=str(uuid.uuid4()),
                    amount=amount,
                    method=method,
                    tx_hash=tx_hash,
                    verified=verified,
                )
                invoice.payments.append(payment)

                if not verified:
                    return payment  # recorded, but contributes nothing

                self.total_paid += amount
                if invoice.is_fully_paid():
                    invoice.status = InvoiceStatus.PAID
                elif invoice.paid_amount() > 0:
                    invoice.status = InvoiceStatus.PARTIALLY_PAID

                return payment
        return None


class AccountsWorker:
    """
    Real accounts management for ACME.

    Handles:
    - Customer lifecycle management
    - Invoice generation with line items
    - Payment tracking
    - Revenue accounting
    - Cash flow management
    """

    def __init__(self, acme_wallet: str, verifier: Optional[PaymentVerifier] = None):
        """
        acme_wallet: the wallet you actually control and can check.
        verifier:    YOUR function that confirms a tx really settled. If you
                     don't pass one, this worker can NEVER count revenue — by
                     design. That is the honest default.
        """
        self.acme_wallet = acme_wallet
        self.verifier = verifier
        self.customers: Dict[str, CustomerAccount] = {}
        self.total_revenue: float = 0.0   # verified settled funds only
        self.total_invoiced: float = 0.0  # what you believe you're owed

    def create_customer(self, name: str, email: str, contract_value: Optional[float] = None) -> CustomerAccount:
        """Create new customer account."""
        customer = CustomerAccount(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            contract_value=contract_value,
        )
        self.customers[customer.id] = customer
        return customer

    def invoice_customer(
        self,
        customer_id: str,
        amount: float,
        description: str,
        line_items: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Invoice]:
        """Create invoice for work completed."""
        customer = self.customers.get(customer_id)
        if not customer:
            return None

        invoice = customer.create_invoice(amount, description, line_items)
        self.total_invoiced += amount
        return invoice

    def record_payment(
        self,
        customer_id: str,
        invoice_id: str,
        amount: float,
        tx_hash: str,
        method: PaymentMethod = PaymentMethod.USDC,
    ) -> Optional[Payment]:
        """
        Record a CLAIMED payment and try to verify it for real.

        Revenue moves only if self.verifier(tx_hash, amount) returns True.
        No verifier configured => the payment is stored as UNVERIFIED and
        adds $0. There is no path here that invents money.
        """
        customer = self.customers.get(customer_id)
        if not customer:
            return None

        verified = False
        if self.verifier is not None and tx_hash:
            verified = bool(self.verifier(tx_hash, amount))

        payment = customer.receive_payment(invoice_id, amount, method, tx_hash, verified)
        if payment and verified:
            self.total_revenue += amount

        return payment

    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute accounting operations."""
        action = parameters.get("action", "status")

        if action == "status":
            return {
                "customers": len(self.customers),
                "total_invoiced": self.total_invoiced,
                "total_received": self.total_revenue,
                "outstanding": self.total_invoiced - self.total_revenue,
                "acme_wallet": self.acme_wallet,
                "status": "complete",
            }

        elif action == "create_customer":
            customer = self.create_customer(
                name=parameters.get("name", ""),
                email=parameters.get("email", ""),
                contract_value=parameters.get("contract_value"),
            )
            return {"customer_id": customer.id, "status": "created"}

        elif action == "invoice":
            invoice = self.invoice_customer(
                customer_id=parameters.get("customer_id", ""),
                amount=parameters.get("amount", 0),
                description=parameters.get("description", ""),
                line_items=parameters.get("line_items"),
            )
            return {
                "invoice_id": invoice.id if invoice else None,
                "status": "created" if invoice else "error",
            }

        elif action == "record_payment":
            tx_hash = parameters.get("tx_hash")
            if not tx_hash:
                return {"status": "error", "reason": "tx_hash required; no fabricated payments"}
            payment = self.record_payment(
                customer_id=parameters.get("customer_id", ""),
                invoice_id=parameters.get("invoice_id", ""),
                amount=parameters.get("amount", 0),
                tx_hash=tx_hash,
                method=PaymentMethod(parameters.get("method", "usdc")),
            )
            if not payment:
                return {"status": "error"}
            return {
                "payment_id": payment.id,
                "verified": payment.verified,
                "counted_as_revenue": payment.verified,
                "status": "verified" if payment.verified else "recorded_unverified",
            }

        return {"status": "unknown_action"}

    def get_revenue_summary(self) -> Dict[str, Any]:
        """Get complete financial summary."""
        customers_list = [
            {
                "id": c.id,
                "name": c.name,
                "invoiced": c.total_invoiced,
                "paid": c.total_paid,
                "outstanding": c.total_invoiced - c.total_paid,
                "payment_rate": f"{c.payment_rate():.1f}%",
                "invoices": c.invoice_count(),
            }
            for c in self.customers.values()
        ]

        return {
            "total_customers": len(self.customers),
            "total_invoiced": self.total_invoiced,
            "total_received": self.total_revenue,
            "outstanding_receivables": self.total_invoiced - self.total_revenue,
            "collection_rate": f"{(self.total_revenue / self.total_invoiced * 100) if self.total_invoiced > 0 else 0:.1f}%",
            "acme_wallet": self.acme_wallet,
            "customers": customers_list,
        }

    def get_customer(self, customer_id: str) -> Optional[CustomerAccount]:
        """Get customer account."""
        return self.customers.get(customer_id)
