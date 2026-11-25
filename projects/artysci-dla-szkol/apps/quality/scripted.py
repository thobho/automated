"""Scripted profile (US-11.2): a deterministic profile built only from `build_input` data, with no
AI. It is valid against the profile JSON Schema and clean for the hard-rule validator, so it can be
the reply of `FakeClient` in tests of the generation job (here and in T43 to T45).

    reply = json.dumps(scripted_profile(build_input(artist)))
    client = FakeClient(reply=reply)

It copies facts and names and never invents a number, a price or a claim. It picks the first photo
that may be the main one, reports what is missing in `gaps` (`no_price`, `no_main_photo`,
`no_photos`, `no_video`) and leaves testimonials empty.
"""

from apps.artists.models import ArtistType, Audience

THEMES = {
    "theatre": "burgundy_light",
    "illusion": "navy_gold",
    "music": "coral_dark",
    "science_show": "cream_green",
    "animal_show": "cream_green",
    "workshops": "cream_green",
}
FACT_MAX = 22  # validator: FACT_MAX_CHARS
LIMIT_DESCRIPTION = 800  # validator: description.paragraph


def _cut(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _list(items: list[str]) -> str:
    return ", ".join(items)


def scripted_profile(input_data: dict) -> dict:
    artist = input_data["artist"]
    questionnaire = input_data["questionnaire"]
    offers = input_data["offers"]
    name, city = artist["name"], artist["city"]
    type_label = str(ArtistType(artist["type"]).label) if artist["type"] else ""
    # Labels such as "klasy 0–3" hold numbers that are not in the artist's own texts.
    audiences = [
        label
        for label in (str(Audience(a).label) for a in artist["audiences"])
        if not any(ch.isdigit() for ch in label)
    ]

    photos = [p for p in input_data["photos"] if p["can_be_main"]]
    frames = [f for v in input_data["videos"] for f in v["frames"] if f["can_be_main"]]
    main = (photos or frames or [None])[0]
    gallery_photos = [p["id"] for p in photos]
    video_ids = [v["id"] for v in input_data["videos"]]

    facts = [{"label": "Miasto", "value": _cut(city, FACT_MAX)}] if city else []
    age_from, age_to = questionnaire["q_age_from"], questionnaire["q_age_to"]
    age_range = f"{age_from}–{age_to} lat" if age_from is not None and age_to is not None else ""
    if age_range:
        facts.append({"label": "Wiek", "value": age_range})
    if questionnaire["q_duration_minutes"]:
        facts.append({"label": "Czas", "value": f"{questionnaire['q_duration_minutes']} min"})
    if questionnaire["q_max_audience"]:
        facts.append({"label": "Widzów", "value": f"do {questionnaire['q_max_audience']}"})

    titles = [offer["title"] for offer in offers]
    intro = f"{name} to {type_label}" if type_label else name
    intro += f" z miejscowości {city}." if city else "."
    paragraph = intro
    if titles:
        paragraph += f" W repertuarze: {_list(titles)}."
    paragraphs = [_cut(paragraph, LIMIT_DESCRIPTION)]
    site = " ".join(input_data["site_text"].split())
    if site:  # the first sentence of the artist's own text, copied
        paragraphs.append(_cut(site.split(". ")[0].rstrip(".") + ".", LIMIT_DESCRIPTION))

    requirements = [
        _cut(questionnaire[key], 160)
        for key in ("q_tech_room", "q_tech_power", "q_tech_sound")
        if questionnaire[key]
    ]
    faq = []
    if questionnaire["q_duration_minutes"]:
        faq.append(
            {
                "question": "Ile trwa występ?",
                "answer": f"Około {questionnaire['q_duration_minutes']} minut.",
            }
        )
    if questionnaire["q_tech_room"]:
        faq.append(
            {
                "question": "Czego potrzeba na miejscu?",
                "answer": _cut(questionnaire["q_tech_room"], 500),
            }
        )

    has_price = (
        any(o["price_pln"] or o["price_on_request"] for o in offers)
        or questionnaire["q_price_from_pln"]
        or questionnaire["q_price_to_pln"]
        or questionnaire["q_price_on_request"]
    )
    gaps = []
    if not has_price:
        gaps.append({"code": "no_price", "message": "Podaj cenę albo zaznacz „na zapytanie”."})
    if main is None:
        gaps.append({"code": "no_main_photo", "message": "Dodaj zdjęcie, które może być główne."})
    if not input_data["photos"]:
        gaps.append({"code": "no_photos", "message": "Dodaj zdjęcia z występów."})
    if not input_data["videos"]:
        gaps.append({"code": "no_video", "message": "Dodaj link do filmu z występu."})

    subheadline = _cut(" · ".join(part for part in (type_label.capitalize(), city) if part), 160)
    return {
        "hero": {
            "headline": _cut(name, 70),
            "subheadline": subheadline,
            "main_photo_id": main["id"] if main else None,
            "button_label": "Sprawdź termin",
        },
        "facts": facts,
        "description": {"paragraphs": paragraphs},
        "schools": {
            "headline": "Dla szkół i przedszkoli",
            "points": [_cut("Dla: " + _list(audiences), 160)]
            if audiences
            else ["Oferta dla szkół i przedszkoli"],
            "age_range": age_range,
            "requirements": requirements,
        },
        "offers": [{"offer_id": o["id"], "tagline": _cut(o["title"], 120)} for o in offers],
        "gallery": {
            "photo_ids": gallery_photos,
            "video_ids": video_ids,
            "captions": [
                {"material_id": pid, "alt": _cut(f"Zdjęcie z występu: {name}", 140)}
                for pid in gallery_photos
            ],
        },
        "testimonials": [],
        "faq": faq,
        "theme": THEMES.get(artist["type"], "cream_green"),
        "seo": {
            "title": _cut(name, 60),
            "description": _cut(f"{intro} Oferta dla szkół i przedszkoli.", 160),
        },
        "gaps": gaps,
        "claims_audit": [{"claim": _cut(name, 200), "source": "basics", "source_id": None}],
    }
