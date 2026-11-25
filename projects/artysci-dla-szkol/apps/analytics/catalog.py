"""Closed catalog of business events: name -> allowed property names.

Adding an event or a property is a code change on purpose: nothing outside this registry can be
recorded, so personal data cannot slip in through a free-form property. Never add properties
that carry e-mails, names, free text or IPs; use ids, counts, enums and durations.
"""

EVENT_CATALOG: dict[str, frozenset[str]] = {
    "artist_registered": frozenset({"source"}),
    "institution_registered": frozenset({"institution_type", "rspo_matched", "linked_existing"}),
    "account_confirmed": frozenset(),
    "institution_verified": frozenset({"method"}),
    # US-2.2: never the URL; status is the import status code, counts and duration only.
    "website_import_started": frozenset(),
    "website_import_finished": frozenset({"status", "page_count", "photo_count", "duration_ms"}),
    "profile_generated": frozenset({"duration_ms", "attempt"}),
    # US-2.8: ids and a whole-number percentage only, no name or slug.
    "profile_published": frozenset({"profile_id", "completeness_percent"}),
    "profile_withdrawn": frozenset({"profile_id"}),
    "inquiry_sent": frozenset({"inquiry_id", "artist_count"}),
    "inquiry_answered": frozenset({"inquiry_id", "response_hours", "answer"}),
    "offer_accepted": frozenset({"inquiry_id", "response_hours"}),
    "performance_confirmed": frozenset({"inquiry_id"}),
    "notice_published": frozenset({"notice_id"}),
    "notice_applied": frozenset({"notice_id"}),
}
