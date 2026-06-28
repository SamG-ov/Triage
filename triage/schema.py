"""
Phase 2: the structured-output schema for Triage.

We force the model to return data in THIS exact shape instead of free text,
then validate it. If the model returns anything off-spec, validation fails
loudly so we catch it immediately instead of shipping garbage downstream.

Design notes:
  - `category` values are EXACTLY the Bitext dataset's labels, so the model's
    output can be compared directly against ground truth when we score accuracy.
  - `team` is NOT asked of the model. Routing is a fixed business rule, so we
    derive team from category with a lookup table (a dict can't hallucinate).
"""

from enum import Enum

from pydantic import BaseModel, Field, computed_field


class Urgency(str, Enum):
    """How quickly a human should respond, ordered low -> urgent."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Category(str, Enum):
    """Ticket category. Values match the Bitext dataset's `category` column."""

    ACCOUNT = "ACCOUNT"
    ORDER = "ORDER"
    REFUND = "REFUND"
    INVOICE = "INVOICE"
    CONTACT = "CONTACT"
    PAYMENT = "PAYMENT"
    FEEDBACK = "FEEDBACK"
    DELIVERY = "DELIVERY"
    SHIPPING = "SHIPPING"
    SUBSCRIPTION = "SUBSCRIPTION"
    CANCEL = "CANCEL"


class Team(str, Enum):
    """The support queue a ticket is routed to."""

    ACCOUNT_MANAGEMENT = "Account Management"
    BILLING = "Billing"
    ORDERS = "Orders"
    LOGISTICS = "Logistics"
    CUSTOMER_RELATIONS = "Customer Relations"


# Fixed routing policy: each category maps to exactly one team. This is a
# business rule, so we encode it once here rather than asking the LLM to guess.
CATEGORY_TO_TEAM: dict[Category, Team] = {
    Category.ACCOUNT: Team.ACCOUNT_MANAGEMENT,
    Category.ORDER: Team.ORDERS,
    Category.DELIVERY: Team.LOGISTICS,
    Category.SHIPPING: Team.LOGISTICS,
    Category.REFUND: Team.BILLING,
    Category.INVOICE: Team.BILLING,
    Category.PAYMENT: Team.BILLING,
    Category.SUBSCRIPTION: Team.BILLING,
    Category.CANCEL: Team.BILLING,
    Category.FEEDBACK: Team.CUSTOMER_RELATIONS,
    Category.CONTACT: Team.CUSTOMER_RELATIONS,
}


def team_for_category(category: Category) -> Team:
    """Look up the routing team for a category. KeyError if unmapped (a bug)."""
    return CATEGORY_TO_TEAM[category]


class TicketClassification(BaseModel):
    """
    The structured result of classifying ONE ticket.

    `urgency` and `category` are produced by the model (these two fields ARE
    the tool schema we hand to Claude). `team` is computed from `category`, so
    it is always consistent and never something the model can get wrong.
    """

    urgency: Urgency = Field(description="How quickly a human should respond.")
    category: Category = Field(description="The single best-fitting category.")

    @computed_field  # included when we serialize, but NOT asked of the model
    @property
    def team(self) -> Team:
        return team_for_category(self.category)
