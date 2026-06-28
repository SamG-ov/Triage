"""
Phase 2 tests: prove the schema accepts good data and REJECTS bad data.

The whole point of validation is that malformed model output fails loudly
(raises an error) instead of silently flowing downstream. These tests lock
that behaviour in.
"""

import pytest
from pydantic import ValidationError

from triage.schema import (
    Category,
    Team,
    TicketClassification,
    Urgency,
    team_for_category,
)


def test_valid_classification_parses_and_derives_team():
    # Strings come in (as they would from the model), enums come out.
    c = TicketClassification(urgency="high", category="REFUND")
    assert c.urgency is Urgency.HIGH
    assert c.category is Category.REFUND
    assert c.team is Team.BILLING  # derived from category, not supplied


def test_every_category_routes_to_a_team():
    # If any category lacked a team, routing would silently break for it.
    for category in Category:
        assert isinstance(team_for_category(category), Team)


def test_unknown_urgency_fails_loudly():
    with pytest.raises(ValidationError):
        TicketClassification(urgency="super-urgent", category="REFUND")


def test_unknown_category_fails_loudly():
    # "BILLING" is a TEAM concept, not a valid category label -> must reject.
    with pytest.raises(ValidationError):
        TicketClassification(urgency="low", category="BILLING")


def test_serialization_includes_derived_team():
    c = TicketClassification(urgency="medium", category="DELIVERY")
    dumped = c.model_dump()
    assert dumped["team"] == Team.LOGISTICS
