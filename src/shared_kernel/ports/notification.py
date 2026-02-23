"""
src/shared_kernel/ports/notification.py
=========================================
Notification CHANNEL enum and PAYLOAD value object only.

══════════════════════════════════════════════════
GOLDEN RULE: NotificationSender Protocol is NOT here.
══════════════════════════════════════════════════

Each consuming context defines its own notification port in:
    src/contexts/<context>/application/ports/outbound.py

Why:
  - Assignments notify "deadline in N hours" (simple).
  - Exams notify "exam in N hours, room X, duration Y mins" (richer).
  - Putting one shared Protocol here forces both to the same contract NOW,
    before requirements are fully known — a premature coupling.
  - The concrete TelegramAdapter implements both context-local Protocols.
    Structural typing (Protocol) means no inheritance needed.

What stays here:
  - NotificationChannel enum (adapters use it to route delivery).
  - NotificationPayload (adapter-layer value object; domain never touches it).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class NotificationChannel(Enum):
    """Delivery channel. Used by adapter implementations only."""
    EMAIL = auto()
    TELEGRAM = auto()
    PUSH = auto()
    SMS = auto()


@dataclass(frozen=True)
class NotificationPayload:
    """Generic payload used at the adapter layer to route and send messages.

    Application/domain layers never construct this.
    Each context's outbound port defines typed notification methods.
    Adapters translate those calls into NotificationPayload for delivery.
    """
    channel: NotificationChannel
    recipient_reference: str   # Telegram chat_id, email address, etc.
    subject: str
    body: str
