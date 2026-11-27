"""Catalog filters in the URL (US-4.2): parsing, matching, the page, events."""

from datetime import timedelta

import pytest
from django.test import Client
from django.utils import timezone

from apps.accounts.tests.conftest import make_artist
from apps.analytics.models import Event
from apps.artists.models import Artist, PublicationStatus
from apps.catalog import filters, listing, services
from apps.catalog.filters import Filters
from apps.catalog.models import CatalogEntry, EntryKind

pytestmark = pytest.mark.django_db

URL = "/artysci/"
_counter = iter(range(1, 1000))


def make(name, **fields) -> Artist:
    n = next(_counter)
    artist = Artist.objects.get(user=make_artist(f"f{n}@example.invalid"))
    artist.name = name
    artist.slug = f"a-{n}"
    artist.publication_status = PublicationStatus.PUBLISHED
    artist.save()
    CatalogEntry.objects.create(
        artist=artist,
        slug=artist.slug,
        name=name,
        published_at=timezone.now() - timedelta(minutes=n),
        **fields,
    )
    return artist


def names(response) -> list[str]:
    return [c.name for c in response.context["page"].cards]


def get(query=""):
    return Client().get(URL + query)


# --- parsing ------------------------------------------------------------------------------------


def test_parse_keeps_known_values_and_drops_unknown_ones():
    f = filters.parse(
        {
            "wojewodztwo": "lodzkie",
            "rodzaj": "theatre",
            "wiek": "grades_0_3",
            "tematyka": "hejt",
            "forma": "spektakl",
            "cena_max": "1000",
            "czas_max": "60",
        }
    )
    assert f.active() == {
        "wojewodztwo": "lodzkie",
        "rodzaj": "theatre",
        "wiek": "grades_0_3",
        "tematyka": "hejt",
        "forma": "spektakl",
        "cena_max": 1000,
        "czas_max": 60,
    }


@pytest.mark.parametrize(
    "params",
    [
        {"wojewodztwo": "xyz"},
        {"rodzaj": "<script>"},
        {"wiek": "nope"},
        {"tematyka": "nie-ma"},
        {"forma": "nie-ma"},
        {"cena_max": "abc"},
        {"cena_max": "-5"},
        {"cena_max": "0"},
        {"cena_max": "1e3"},
        {"cena_max": "9" * 30},
        {"czas_max": "٣"},  # a non-ASCII digit
        {"czas_max": "1.5"},
    ],
)
def test_parse_ignores_bad_values(params):
    assert filters.parse(params).active() == {}


def test_inactive_dictionary_entry_is_ignored():
    entry = services.add_entry(EntryKind.TOPIC, "Stara tematyka")
    assert filters.parse({"tematyka": entry.slug}).tematyka == entry.slug
    services.deactivate_entry(entry)
    assert filters.parse({"tematyka": entry.slug}).tematyka == ""


def test_url_and_without():
    f = Filters(rodzaj="theatre", cena_max=500)
    assert f.url() == "/artysci/?rodzaj=theatre&cena_max=500"
    assert f.url(page=1) == f.url()
    assert f.url(page=3) == "/artysci/?rodzaj=theatre&cena_max=500&strona=3"
    assert f.without("rodzaj").url() == "/artysci/?cena_max=500"
    assert Filters().url() == "/artysci/"


@pytest.mark.parametrize(
    ("count", "text"),
    [
        (0, "Znaleziono 0 artystów"),
        (1, "Znaleziono 1 artystę"),
        (2, "Znaleziono 2 artystów"),
        (5, "Znaleziono 5 artystów"),
        (22, "Znaleziono 22 artystów"),
    ],
)
def test_found_text(count, text):
    assert filters.found_text(count) == text


# --- matching -----------------------------------------------------------------------------------


def test_voivodeship_matches_the_area_not_the_city():
    make("A", voivodeships=["lodzkie"])
    make("B", voivodeships=["mazowieckie"])
    assert names(get("?wojewodztwo=lodzkie")) == ["A"]


def test_type_age_topic_and_form_filters():
    make(
        "Teatr",
        artist_type="theatre",
        age_groups=["grades_0_3"],
        topics=[{"slug": "hejt", "name": "Hejt"}],
    )
    make("Muzyka", artist_type="music", forms=[{"slug": "warsztaty", "name": "Warsztaty"}])
    assert names(get("?rodzaj=music")) == ["Muzyka"]
    assert names(get("?wiek=grades_0_3")) == ["Teatr"]
    assert names(get("?tematyka=hejt")) == ["Teatr"]
    assert names(get("?forma=warsztaty")) == ["Muzyka"]


def test_filters_combine_with_and():
    make("A", artist_type="theatre", voivodeships=["lodzkie"])
    make("B", artist_type="music", voivodeships=["lodzkie"])
    make("C", artist_type="theatre", voivodeships=["slaskie"])
    assert names(get("?rodzaj=theatre&wojewodztwo=lodzkie")) == ["A"]


def test_offer_filter_uses_the_same_offer_for_price_and_time():
    make("A", offers=[{"price": 900, "duration": 60}])
    make("B", offers=[{"price": 900, "duration": 120}, {"price": None, "duration": 45}])
    assert names(get("?cena_max=1000&czas_max=60")) == ["A"]
    assert sorted(names(get("?cena_max=1000"))) == ["A", "B"]
    assert sorted(names(get("?czas_max=60"))) == ["A", "B"]  # B: the on-request offer lasts 45


def test_offer_without_price_or_duration_does_not_match():
    make("Zapytanie", offers=[{"price": None, "duration": 30}])
    make("BezCzasu", offers=[{"price": 100, "duration": None}])
    assert names(get("?cena_max=5000")) == ["BezCzasu"]
    assert names(get("?czas_max=500")) == ["Zapytanie"]
    assert names(get("?cena_max=5000&czas_max=500")) == []


def test_price_limit_is_inclusive():
    make("A", offers=[{"price": 1000, "duration": None}])
    assert names(get("?cena_max=1000")) == ["A"]
    assert names(get("?cena_max=999")) == []


def test_only_published_artists_are_listed():
    artist = make("Ukryty", voivodeships=["lodzkie"])
    Artist.objects.filter(pk=artist.pk).update(publication_status=PublicationStatus.WITHDRAWN)
    assert names(get("?wojewodztwo=lodzkie")) == []


# --- the page -----------------------------------------------------------------------------------


def test_form_shows_the_current_values():
    make("A")
    html = get("?wojewodztwo=lodzkie&cena_max=700&czas_max=45").content.decode()
    assert '<option value="lodzkie" selected>' in html
    assert 'value="700"' in html and 'value="45"' in html
    assert 'name="rodzaj"' in html and "dowolny" in html


def test_bad_values_give_200_full_list_and_are_not_echoed():
    make("A")
    response = get("?wojewodztwo=xyz&cena_max=abc")
    assert response.status_code == 200
    assert names(response) == ["A"]
    body = response.content.decode()
    assert "xyz" not in body and "abc" not in body
    assert not Event.objects.exists()  # no valid filter: not a filtered search


def test_count_line():
    make("A")
    make("B")
    assert "Znaleziono 2 artystów" in get().content.decode()
    make("C", artist_type="music")
    assert "Znaleziono 1 artystę" in get("?rodzaj=music").content.decode()


def test_pagination_keeps_filters():
    for i in range(listing.PAGE_SIZE + 3):
        make(f"T{i}", artist_type="theatre", topics=[{"slug": "hejt", "name": "Hejt"}])
    make("Inny", artist_type="music")
    body = get("?rodzaj=theatre&tematyka=hejt").content.decode()
    assert "?rodzaj=theatre&amp;tematyka=hejt&amp;strona=2" in body
    page2 = get("?rodzaj=theatre&tematyka=hejt&strona=2")
    assert page2.status_code == 200 and len(names(page2)) == 3
    assert "?rodzaj=theatre&amp;tematyka=hejt" in page2.content.decode()
    assert get("?rodzaj=music&strona=2").status_code == 404


def test_empty_results_offer_wider_filters_and_the_notice_button():
    make("A", voivodeships=["slaskie"])
    response = get("?wojewodztwo=lodzkie&cena_max=100")
    body = response.content.decode()
    assert response.status_code == 200 and names(response) == []
    assert "Znaleziono 0 artystów" in body
    assert "Wyczyść filtry" in body
    assert 'href="/artysci/?cena_max=100"' in body  # drops only wojewodztwo
    assert 'href="/artysci/?wojewodztwo=lodzkie"' in body  # drops only cena_max
    assert "Opublikuj ogłoszenie, a artyści zgłoszą się sami" in body
    assert (
        'href="/ogloszenia/nowe/?wojewodztwo=lodzkie&amp;cena_max=100&amp;zrodlo=katalog"' in body
    )


def test_no_artists_at_all_keeps_the_old_message():
    assert "Nie ma jeszcze żadnych opublikowanych artystów" in get().content.decode()


# --- events -------------------------------------------------------------------------------------


def test_filtered_search_records_one_event_without_personal_data():
    make("A", voivodeships=["lodzkie"], offers=[{"price": 500, "duration": 30}])
    get("?wojewodztwo=lodzkie&cena_max=1000")
    (event,) = Event.objects.all()
    assert event.name == "catalog_searched"
    assert event.properties == {
        "wojewodztwo": "lodzkie",
        "cena_max": 1000,
        "result_count": 1,
        "page": 1,
    }
    assert event.actor == "" and event.object_id == ""


def test_unfiltered_list_records_nothing():
    make("A")
    get()
    assert not Event.objects.exists()


def test_empty_result_records_search_and_no_results():
    get("?rodzaj=theatre")
    assert sorted(Event.objects.values_list("name", flat=True)) == [
        "catalog_no_results",
        "catalog_searched",
    ]
    no_results = Event.objects.get(name="catalog_no_results")
    assert no_results.properties == {"rodzaj": "theatre"}
    assert Event.objects.get(name="catalog_searched").properties["result_count"] == 0


def test_head_request_records_nothing():
    Client().head(URL + "?rodzaj=theatre")
    assert not Event.objects.exists()
