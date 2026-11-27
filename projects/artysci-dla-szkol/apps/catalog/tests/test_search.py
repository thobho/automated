"""Polish text search of the catalog (US-4.3): stems, typos, ranking, published data only, privacy.

These tests run on whatever database the run uses; with `DATABASE_URL` they run on PostgreSQL (CI).
"""

import logging

import pytest
from django.test import Client

from apps.analytics.models import Event
from apps.artists.models import Offer
from apps.catalog import listing, search, services
from apps.catalog.filters import Filters
from apps.catalog.models import CatalogEntry, DictionaryEntry, EntryKind
from apps.profiles import publication
from apps.profiles.tests.test_publication import make_ready

pytestmark = pytest.mark.django_db

URL = "/artysci/"


def publish(email, name, offers=(), topics=()):
    artist = make_ready(email, name)
    if offers:  # without titles the neutral seed offer stays (a page needs an offer to publish)
        Offer.objects.filter(artist=artist).delete()
    for position, title in enumerate(offers):
        Offer.objects.create(
            artist=artist, title=title, description="x", position=position, price_pln=500
        )
    if topics:
        entries = [  # the starting dictionary already has some of the names
            DictionaryEntry.objects.filter(kind=EntryKind.TOPIC, name=t).first()
            or services.add_entry(EntryKind.TOPIC, t)
            for t in topics
        ]
        services.set_artist_entries(artist, EntryKind.TOPIC, entries)
    return publication.publish(artist)


def found(q, **extra) -> list[str]:
    page = listing.cards_page(None, Filters(q=q, **extra))
    return [c.name for c in page.cards]


# --- the pure helpers ----------------------------------------------------------------------------


def test_folding_and_function_words():
    assert search.words("Spektakl o hejcie, na Łódź i w Żyrardowie") == [
        "spektakl",
        "hejcie",
        "lodz",
        "zyrardowie",
    ]


@pytest.mark.parametrize(
    "a,b",
    [
        ("hejcie", "hejtu"),
        ("uzaleznieniach", "uzaleznienia"),
        ("teatrze", "teatr"),
        ("spektaklu", "spektakl"),
        ("warsztatami", "warsztaty"),
    ],
)
def test_inflected_forms_share_a_stem(a, b):
    assert search.stem(a) == search.stem(b)


def test_short_words_are_not_cut_to_nothing():
    assert search.stem("las") == "las"
    assert search.stem("kot") == "kot"


def test_clean_cuts_to_100_and_collapses_spaces():
    assert search.clean("   ") == ""
    assert search.clean(None) == ""
    assert search.clean("  a   b ") == "a b"
    assert len(search.clean("x" * 300)) == 100


def test_query_with_only_function_words_is_no_search():
    assert search.search(CatalogEntry.objects.all(), "o w na dla i") is None


# --- acceptance criteria -------------------------------------------------------------------------


def test_inflected_offer_title():
    publish("a@example.invalid", "Teatr Iskra", offers=["Cena hejtu"])
    publish("b@example.invalid", "Zespół Inny", offers=["Warsztaty tańca"])
    assert found("spektakl o hejcie") == ["Teatr Iskra"]


def test_diacritics_and_inflected_topic():
    publish("a@example.invalid", "Teatr Iskra", topics=["uzależnienia"])
    publish("b@example.invalid", "Zespół Inny", topics=["ekologia"])
    assert found("uzaleznieniach") == ["Teatr Iskra"]
    assert found("UZALEŻNIENIA") == ["Teatr Iskra"]


def test_one_typo_in_the_name_and_unrelated_artist_stays_out():
    publish("a@example.invalid", "Kolorowa Kreda")
    publish("b@example.invalid", "Zespół Inny", offers=["Warsztaty tańca"])
    assert found("kolorowa kerda") == ["Kolorowa Kreda"]  # swapped pair
    assert found("kolorowa kreta") == ["Kolorowa Kreda"]  # substituted letter
    assert found("kolorowa kreeda") == ["Kolorowa Kreda"]  # extra letter


def test_short_words_do_not_get_typo_tolerance():
    publish("a@example.invalid", "Teatr Las")
    assert found("lsa") == []


def test_unpublished_offer_is_found_only_after_publishing_changes_and_not_after_withdrawal():
    artist = publish("a@example.invalid", "Teatr Iskra", offers=["Cena hejtu"])
    Offer.objects.create(
        artist=artist, title="Las w słoiku", description="x", position=5, price_pln=500
    )
    assert found("słoiku") == []
    publication.update_published(artist)
    assert found("słoiku") == ["Teatr Iskra"]
    publication.withdraw(artist)
    assert found("słoiku") == []


def test_exact_match_before_typo_match_and_ties_keep_the_catalog_order():
    publish("a@example.invalid", "Kreda Magiczna")  # published first
    publish("b@example.invalid", "Kerda Teatr")  # typo only for "kreda"
    publish("c@example.invalid", "Inny Zespół", offers=["Kreda"])
    # name match (100) > offer match (10) > typo-only match (1)
    assert found("kreda") == ["Kreda Magiczna", "Inny Zespół", "Kerda Teatr"]


def test_equal_scores_keep_the_order_of_the_list_without_search():
    first = publish("a@example.invalid", "Kreda Pierwsza")
    second = publish("b@example.invalid", "Kreda Druga")
    plain = [c.name for c in listing.cards_page(None).cards]
    assert found("kreda") == plain
    assert {first.name, second.name} == set(plain)


def test_search_combines_with_filters():
    publish("a@example.invalid", "Teatr Iskra", topics=["ekologia"])
    publish("b@example.invalid", "Teatr Zorza", topics=["historia"])
    assert sorted(found("teatr")) == ["Teatr Iskra", "Teatr Zorza"]
    assert found("teatr", tematyka="ekologia") == ["Teatr Iskra"]


def test_row_is_refreshed_with_the_snapshot_and_rebuild():
    artist = publish("a@example.invalid", "Teatr Iskra", offers=["Cena hejtu"])
    CatalogEntry.objects.filter(artist=artist).update(
        search_name="", search_other="", search_fuzzy=""
    )
    assert found("iskra") == []
    listing.rebuild_all()
    assert found("iskra") == ["Teatr Iskra"]


# --- the page ------------------------------------------------------------------------------------


def test_view_status_for_all_roles_and_empty_query(client):
    publish("a@example.invalid", "Teatr Iskra", offers=["Cena hejtu"])
    for q in ("", "   ", "o w na", "hejcie", "zażółć"):
        assert Client().get(URL, {"q": q}).status_code == 200
    assert "Teatr Iskra" in Client().get(URL, {"q": "spektakl o hejcie"}).content.decode()
    assert "Teatr Iskra" in Client().get(URL, {"q": "  "}).content.decode()


def test_view_escapes_and_cuts_the_text():
    publish("a@example.invalid", "Teatr Iskra")
    html = Client().get(URL, {"q": "<script>alert(1)</script>"}).content.decode()
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html
    response = Client().get(URL, {"q": "x" * 300})
    assert response.status_code == 200
    assert "x" * 101 not in response.content.decode()
    assert "x" * 100 in response.content.decode()


def test_pagination_keeps_q_and_filters():
    for number in range(30):
        publish(f"p{number}@example.invalid", f"Kreda {number:02d}")
    html = Client().get(URL, {"q": "kreda"}).content.decode()
    assert "q=kreda&amp;strona=2" in html or "q=kreda&strona=2" in html
    assert Client().get(URL, {"q": "kreda", "strona": "2"}).status_code == 200
    assert Client().get(URL, {"q": "kreda", "strona": "3"}).status_code == 404


def test_search_box_is_on_the_page_and_keeps_its_value():
    html = Client().get(URL, {"q": "hejcie"}).content.decode()
    assert 'name="q"' in html and 'value="hejcie"' in html


def test_empty_result_does_not_pass_the_text_to_the_notice_page():
    publish("a@example.invalid", "Teatr Iskra")
    html = Client().get(URL, {"q": "nieistniejace"}).content.decode()
    assert "/ogloszenia/nowe/" in html
    assert (
        "ogloszenia/nowe/?q=" not in html
        and "q=nieistniejace" not in html.split("catalog-empty")[1]
    )


# --- privacy -------------------------------------------------------------------------------------


def test_text_is_neither_logged_nor_recorded(caplog):
    publish("a@example.invalid", "Teatr Iskra")
    secret = "Jan Kowalski Warszawa"
    with caplog.at_level(logging.DEBUG):
        Client().get(URL, {"q": secret})
    assert "Kowalski" not in caplog.text
    events = list(Event.objects.values("name", "properties"))
    assert "Kowalski" not in str(events)
    searched = Event.objects.get(name="catalog_searched")
    assert searched.properties["text_query"] is True
    assert searched.properties["word_count"] == 3
    assert "q" not in searched.properties


def test_filter_only_search_has_no_text_properties():
    publish("a@example.invalid", "Teatr Iskra")
    Client().get(URL, {"rodzaj": "theatre"})
    props = Event.objects.get(name="catalog_searched").properties
    assert "text_query" not in props and "word_count" not in props
