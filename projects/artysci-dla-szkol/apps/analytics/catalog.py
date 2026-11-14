"""Closed catalog of business events: name -> allowed property names.

Adding an event or a property is a code change on purpose: nothing outside this registry can be
recorded, so personal data cannot slip in through a free-form property. Never add properties
that carry e-mails, names, free text or IPs; use ids, counts, enums and durations.
"""

EVENT_CATALOG: dict[str, frozenset[str]] = {
    "artist_registered": frozenset({"source"}),
    "profile_generated": frozenset({"duration_ms", "attempt"}),
    "profile_published": frozenset({"profile_id"}),
    "inquiry_sent": frozenset({"inquiry_id", "artist_count"}),
    "inquiry_answered": frozenset({"inquiry_id", "response_hours", "answer"}),
    "offer_accepted": frozenset({"inquiry_id", "response_hours"}),
    "performance_confirmed": frozenset({"inquiry_id"}),
    "notice_published": frozenset({"notice_id"}),
    "notice_applied": frozenset({"notice_id"}),
}
