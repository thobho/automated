"""Artist registration (US-1.1) and the profile wizard (US-2.1). Views parse the request,
call `services`, render a response."""

from dataclasses import asdict
from functools import wraps

from django import forms
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_POST

from apps.accounts.permissions import role_required
from apps.core.regions import Voivodeship
from apps.core.uploads import KINDS, MB, UploadRejected
from apps.trust import services as trust
from apps.trust.errors import NoPublishedVersion, StaleWording
from apps.trust.models import STATEMENT_KINDS, BillingForm

from . import materials, resumable, services, website_import
from .models import (
    MAX_AGE,
    ArtistType,
    Audience,
    Material,
    MaterialKind,
    Offer,
    WebsiteImport,
)
from .services import Registration


class ArtistRegistrationForm(forms.Form):
    email = forms.EmailField(label=_("Adres e-mail"), max_length=254)
    name = forms.CharField(label=_("Nazwa"), max_length=200)
    accept = forms.BooleanField(
        required=True,
        error_messages={
            "required": _("Aby założyć konto, zaakceptuj regulamin i politykę prywatności.")
        },
    )


def _form_page(request, form, *, status=200, unavailable=False):
    context = {"form": form, "unavailable": unavailable}
    return render(request, "artists/register.html", context, status=status)


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
def register(request):
    """The registration form. The answer to a valid form is the same for a new and an
    existing address (no enumeration)."""
    if request.method != "POST":
        return _form_page(request, ArtistRegistrationForm())
    form = ArtistRegistrationForm(request.POST)
    if not form.is_valid():
        return _form_page(request, form, status=400)
    email = form.cleaned_data["email"]
    result = services.register_artist(
        email,
        form.cleaned_data["name"],
        request.META.get("REMOTE_ADDR", ""),
        link_base=request.build_absolute_uri("/"),
    )
    if result is Registration.UNAVAILABLE:
        return _form_page(request, form, status=503, unavailable=True)
    context = {
        "email": email,
        "next": reverse("artists:start"),
        "rate_limited": result is Registration.RATE_LIMITED,
    }
    status = 429 if result is Registration.RATE_LIMITED else 200
    return render(request, "artists/register_sent.html", context, status=status)


# --- profile wizard (US-2.1) -----------------------------------------------------------------


class BasicsForm(forms.Form):
    """Step 1. Choice fields refuse values outside the lists (tampered POST)."""

    artist_type = forms.ChoiceField(
        label=_("Rodzaj"),
        choices=ArtistType.choices,
        widget=forms.RadioSelect,
        error_messages={"required": _("Wybierz rodzaj.")},
    )
    name = forms.CharField(
        label=_("Nazwa (imię i nazwisko, zespół lub firma)"),
        max_length=200,
        error_messages={"required": _("Podaj nazwę.")},
    )
    city = forms.CharField(
        label=_("Miasto"), max_length=100, error_messages={"required": _("Podaj miasto.")}
    )
    voivodeships = forms.MultipleChoiceField(
        label=_("Województwa działania"),
        choices=Voivodeship.choices,
        widget=forms.CheckboxSelectMultiple,
        error_messages={"required": _("Wybierz co najmniej jedno województwo.")},
    )
    audiences = forms.MultipleChoiceField(
        label=_("Odbiorcy"),
        choices=Audience.choices,
        widget=forms.CheckboxSelectMultiple,
        error_messages={"required": _("Wybierz co najmniej jedną grupę odbiorców.")},
    )


def _artist(request):
    return services.artist_for(request.user)  # role_required("artist") => never None


@role_required("artist")
def start(request):
    """Wizard overview (`can_create_artist_profile`): step 1 is required, later steps open
    once it is done and can be skipped."""
    artist = _artist(request)
    context = {"steps": services.wizard_steps(artist), "artist": artist}
    return render(request, "artists/start.html", context)


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
@role_required("artist")
def basics(request):
    """Step 1, the basics; prefilled on every visit."""
    artist = _artist(request)
    if request.method != "POST":
        initial = asdict(services.basics_of(artist))
        form = BasicsForm(initial={k: v or None for k, v in initial.items()})
        return render(request, "artists/basics.html", {"form": form})
    form = BasicsForm(request.POST)
    if not form.is_valid():
        return render(request, "artists/basics.html", {"form": form}, status=400)
    services.save_basics(request.user, form.cleaned_data)
    messages.success(request, _("Zapisano dane podstawowe."))
    return redirect("artists:start")


def _basics_required(view):
    """Later wizard steps open only with complete basics (#117 rule); else back to step 1."""

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not services.basics_complete(_artist(request)):
            messages.info(request, _("Najpierw uzupełnij dane podstawowe."))
            return redirect("artists:basics")
        return view(request, *args, **kwargs)

    return wrapper


# --- wizard step "Materiały i kwestionariusz" (US-2.3A) ---------------------------------------

UPLOAD_KINDS = {
    MaterialKind.PHOTO: {
        "accept": "image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp",
        "formats": "JPG, PNG, WebP",
        "url": "artists:materials_photos",
    },
    MaterialKind.PDF: {
        "accept": "application/pdf,.pdf",
        "formats": "PDF",
        "url": "artists:materials_pdfs",
    },
    # video and audio: resumable uploads through materials.js (US-2.3B)
    MaterialKind.VIDEO: {
        "accept": "video/mp4,video/quicktime,video/webm,.mp4,.mov,.webm",
        "formats": "MP4, MOV, WebM",
        "url": "artists:upload_create",
    },
    MaterialKind.AUDIO: {
        "accept": "audio/mpeg,audio/mp4,audio/x-m4a,audio/wav,audio/x-wav,.mp3,.m4a,.wav",
        "formats": "MP3, M4A, WAV",
        "url": "artists:upload_create",
    },
}


def _upload_box(artist, kind, errors=()):
    max_bytes = KINDS[kind][0]
    options = UPLOAD_KINDS[kind]
    return {
        "kind": kind,
        "limit": materials.limit_for(kind),
        "remaining": materials.remaining(artist, kind),
        "max_bytes": max_bytes,
        "max_mb": max_bytes // MB,
        "errors": list(errors),
        "max_seconds": settings.MEDIA_MAX_DURATION_SECONDS if kind == MaterialKind.VIDEO else 0,
        "max_minutes": settings.MEDIA_MAX_DURATION_SECONDS // 60,
        **options,
        "url": reverse(options["url"]),
    }


def _item(material):
    return {
        "material": material,
        "url": materials.file_url(material),
        "thumbnail": materials.thumbnail_url(material),
        "duration": materials.format_duration(material.duration_seconds),
    }


def _materials_page(request, *, photo_errors=(), pdf_errors=(), link_error="", link_url="",
                    status=200):  # fmt: skip
    artist = _artist(request)
    items = [_item(m) for m in materials.materials_for(artist)]
    context = {
        "items": items,
        "photos": _upload_box(artist, MaterialKind.PHOTO, photo_errors),
        "pdfs": _upload_box(artist, MaterialKind.PDF, pdf_errors),
        "videos": _upload_box(artist, MaterialKind.VIDEO),
        "audio": _upload_box(artist, MaterialKind.AUDIO),
        "link_error": link_error,
        "link_url": link_url,
        "questionnaire_filled": materials.questionnaire_filled(artist),
    }
    return render(request, "artists/materials.html", context, status=status)


@never_cache
@role_required("artist")
@_basics_required
def materials_page(request):
    """Photos, PDFs, video links, video and audio files with their scan and processing
    status; links to the questionnaire."""
    return _materials_page(request)


@never_cache
@role_required("artist")
@require_POST
@_basics_required
def materials_upload(request, kind):
    """POST one or more files of `kind` (field ``files``). All must fit the remaining count,
    else nothing is stored; then each file is stored or refused on its own."""
    files = request.FILES.getlist("files")
    errors_key = "photo_errors" if kind == MaterialKind.PHOTO else "pdf_errors"
    if not files:
        return _materials_page(request, status=400, **{errors_key: [_("Wybierz plik.")]})
    artist = _artist(request)
    try:
        materials.check_room(artist, kind, len(files))
    except materials.MaterialRejected as exc:
        return _materials_page(request, status=400, **{errors_key: [exc.message]})
    errors, added = [], 0
    for file in files:
        try:
            materials.add_file(artist, kind, file)
        except (UploadRejected, materials.MaterialRejected) as exc:
            errors.append(f"{materials.clean_name(file.name)}: {exc.message}")
        else:
            added += 1
    if added:
        messages.success(
            request, _("Dodano plików: %(n)d. Sprawdzamy je, zanim zostaną użyte.") % {"n": added}
        )
    if errors:
        return _materials_page(request, status=400, **{errors_key: errors})
    return redirect("artists:materials")


@never_cache
@role_required("artist")
@require_POST
@_basics_required
def materials_link(request):
    """POST ``url``: a YouTube or Vimeo link, checked through the provider's oEmbed."""
    url = request.POST.get("url", "").strip()[:500]
    try:
        materials.add_link(_artist(request), url)
    except materials.MaterialRejected as exc:
        return _materials_page(request, status=400, link_error=exc.message, link_url=url)
    messages.success(request, _("Dodano film."))
    return redirect("artists:materials")


@role_required("artist")
@require_POST
@_basics_required
def material_delete(request, material_id):
    """POST deletes the artist's own material (and its file); another artist's id is 404."""
    try:
        materials.delete_material(_artist(request), material_id)
    except Material.DoesNotExist as exc:
        raise Http404 from exc
    messages.success(request, _("Usunięto materiał."))
    return redirect("artists:materials")


# --- resumable video / audio uploads (US-2.3B): JSON for static/js/materials.js -------------


def _refused(message, status, **extra):
    return JsonResponse({"error": str(message), **extra}, status=status)


def _session_answer(session, status=200):
    data = {
        **resumable.state(session),
        "url": reverse("artists:upload_chunk", args=[session.pk]),
        "complete_url": reverse("artists:upload_complete", args=[session.pk]),
    }
    return JsonResponse(data, status=status)


@never_cache
@role_required("artist")
@require_POST
@_basics_required
def upload_create(request):
    """POST ``kind`` (video/audio), ``size`` (bytes) and ``name``: opens an upload session
    after the kind, size and count checks (before any byte is sent)."""
    try:
        session = resumable.create_session(
            _artist(request),
            request.POST.get("kind", ""),
            request.POST.get("size"),
            request.POST.get("name", ""),
        )
    except resumable.UploadRefused as exc:
        return _refused(exc.message, exc.status)
    except materials.MaterialRejected as exc:
        return _refused(exc.message, 400)
    return _session_answer(session, status=201)


@never_cache
@role_required("artist")
@require_http_methods(["GET", "HEAD", "POST"])
@_basics_required
def upload_chunk(request, session_id):
    """GET: the received offset (to resume). POST: raw bytes of one chunk, its start in the
    ``Upload-Offset`` header. Another artist's or an expired session is 404."""
    artist = _artist(request)
    try:
        if request.method == "POST":
            session = resumable.append_chunk(
                artist,
                session_id,
                request.headers.get("Upload-Offset"),
                request.META.get("CONTENT_LENGTH"),
                request,
            )
        else:
            session = resumable.get_session(artist, session_id)
    except resumable.SessionGone as exc:
        raise Http404 from exc
    except resumable.UploadRefused as exc:
        return _refused(exc.message, exc.status, offset=exc.offset)
    return _session_answer(session)


@never_cache
@role_required("artist")
@require_POST
@_basics_required
def upload_complete(request, session_id):
    """POST once every byte is there: the file is checked, stored and queued for the scan."""
    try:
        material = resumable.complete(_artist(request), session_id)
    except resumable.SessionGone as exc:
        raise Http404 from exc
    except resumable.UploadRefused as exc:
        return _refused(exc.message, exc.status, offset=exc.offset)
    except (materials.MaterialRejected, UploadRejected) as exc:
        return _refused(exc.message, 400)
    messages.success(request, _("Dodano plik. Sprawdzamy go i przetwarzamy, zanim zostanie użyty."))
    return JsonResponse(
        {"material": material.pk, "redirect": reverse("artists:materials")}, status=201
    )


class QuestionnaireForm(forms.Form):
    """Every field is optional; cross-field rules come from `materials.questionnaire_errors`."""

    q_age_from = forms.IntegerField(
        label=_("Wiek widzów od (lat)"), min_value=0, max_value=MAX_AGE, required=False
    )
    q_age_to = forms.IntegerField(
        label=_("Wiek widzów do (lat)"), min_value=0, max_value=MAX_AGE, required=False
    )
    q_duration_minutes = forms.IntegerField(
        label=_("Czas trwania (minuty)"), min_value=1, max_value=materials.MAX_DURATION,
        required=False,
    )  # fmt: skip
    q_max_audience = forms.IntegerField(
        label=_("Maksymalna liczba widzów"), min_value=1, max_value=materials.MAX_AUDIENCE,
        required=False,
    )  # fmt: skip
    q_tech_room = forms.CharField(label=_("Wymagania: sala"), max_length=500, required=False)
    q_tech_power = forms.CharField(label=_("Wymagania: prąd"), max_length=500, required=False)
    q_tech_sound = forms.CharField(
        label=_("Wymagania: nagłośnienie"), max_length=500, required=False
    )
    q_price_from_pln = forms.IntegerField(
        label=_("Cena od (zł)"), min_value=1, max_value=materials.MAX_PRICE, required=False
    )
    q_price_to_pln = forms.IntegerField(
        label=_("Cena do (zł)"), min_value=1, max_value=materials.MAX_PRICE, required=False
    )
    q_price_on_request = forms.BooleanField(label=_("Cena na zapytanie"), required=False)

    def clean(self):
        cleaned = super().clean()
        for field, message in materials.questionnaire_errors(cleaned).items():
            if field not in self.errors:
                self.add_error(field, message)
        return cleaned


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
@role_required("artist")
@_basics_required
def questionnaire(request):
    """The school questionnaire, prefilled on every visit."""
    artist = _artist(request)
    if request.method != "POST":
        form = QuestionnaireForm(initial=materials.questionnaire_of(artist))
        return render(request, "artists/questionnaire.html", {"form": form})
    form = QuestionnaireForm(request.POST)
    if not form.is_valid():
        return render(request, "artists/questionnaire.html", {"form": form}, status=400)
    try:
        materials.save_questionnaire(artist, form.cleaned_data)
    except materials.InvalidQuestionnaire as exc:  # same rules as the form: never expected
        for field, message in exc.errors.items():
            form.add_error(field, message)
        return render(request, "artists/questionnaire.html", {"form": form}, status=400)
    messages.success(request, _("Zapisano kwestionariusz."))
    return redirect("artists:materials")


# --- wizard step "Import ze strony" (US-2.2) ---------------------------------------------------


class WebsiteImportForm(forms.Form):
    url = forms.CharField(
        label=_("Adres Twojej strony"),
        max_length=2000,
        error_messages={"required": _("Podaj adres strony.")},
    )
    confirm = forms.BooleanField(
        label=_(
            "Oświadczam, że to moja strona i mam prawa do jej treści i zdjęć "
            "(oświadczenie „Prawa do materiałów”)."
        ),
        error_messages={
            "required": _("Zaznacz, że strona jest Twoja i masz prawa do jej treści i zdjęć.")
        },
    )


def _import_page(request, form, *, status=200):
    artist = _artist(request)
    context = {
        "form": form,
        "imports": website_import.imports_for(artist)[:5],
        "max_pages": settings.WEBSITE_IMPORT_MAX_PAGES,
        "max_mb": settings.WEBSITE_IMPORT_MAX_BYTES // MB,
        "page_timeout": int(settings.WEBSITE_IMPORT_PAGE_TIMEOUT),
    }
    return render(request, "artists/website_import.html", context, status=status)


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
@role_required("artist")
@_basics_required
def website_import_view(request):
    """The URL and the rights checkbox; POST queues an import and shows its status page."""
    if request.method != "POST":
        return _import_page(request, WebsiteImportForm())
    form = WebsiteImportForm(request.POST)
    if not form.is_valid():
        return _import_page(request, form, status=400)
    try:
        record = website_import.start_import(
            _artist(request), form.cleaned_data["url"], rights_confirmed=True
        )
    except website_import.ImportRefused as exc:
        form.add_error(None, exc.message)
        return _import_page(request, form, status=400)
    return redirect("artists:website_import_status", import_id=record.pk)


@never_cache
@role_required("artist")
@_basics_required
def website_import_status(request, import_id):
    """Status and result of the artist's own import; another artist's id is 404."""
    try:
        record = website_import.get_import(_artist(request), import_id)
    except WebsiteImport.DoesNotExist as exc:
        raise Http404 from exc
    context = {
        "record": record,
        "materials": website_import.imported_materials(record),
        "refresh": not record.finished,
    }
    return render(request, "artists/website_import_status.html", context)


# --- wizard step "Oświadczenia" (US-8.2) ------------------------------------------------------


class DateInput(forms.DateInput):
    input_type = "date"


class StatementForm(forms.Form):
    """One statement per submit. `document` is the wording version the page showed."""

    kind = forms.ChoiceField(choices=[(k, k) for k in STATEMENT_KINDS])
    action = forms.ChoiceField(choices=[("make", "make"), ("withdraw", "withdraw")])
    document = forms.IntegerField(required=False)
    confirm = forms.BooleanField(required=False)
    billing_form = forms.ChoiceField(
        label=_("Forma rozliczenia"),
        choices=BillingForm.choices,
        widget=forms.RadioSelect,
        required=False,
        error_messages={"invalid_choice": _("Wybierz fakturę albo rachunek.")},
    )
    valid_until = forms.DateField(
        label=_("Polisa ważna do (opcjonalnie)"), required=False, widget=DateInput
    )

    def __init__(self, *args, today=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.today = today

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("action") != "make" or "kind" not in cleaned:
            return cleaned
        kind = cleaned["kind"]
        if not cleaned.get("confirm"):
            self.add_error("confirm", _("Zaznacz, że składasz to oświadczenie."))
        if kind == trust.Kind.BILLING_FORM:
            if not cleaned.get("billing_form") and "billing_form" not in self.errors:
                self.add_error("billing_form", _("Wybierz fakturę albo rachunek."))
        else:
            cleaned["billing_form"] = ""
        if kind != trust.Kind.INSURANCE:
            cleaned["valid_until"] = None
        elif cleaned.get("valid_until") and self.today and cleaned["valid_until"] < self.today:
            self.add_error("valid_until", _("Data ważności nie może być z przeszłości."))
        return cleaned


def _statements_page(request, *, form=None, error_kind="", status=200):
    context = {
        "states": trust.statement_overview(_artist(request)),
        "form": form,
        "error_kind": error_kind,
        "billing_choices": BillingForm.choices,
    }
    return render(request, "artists/statements.html", context, status=status)


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
@role_required("artist")
@_basics_required
def statements(request):
    """Each statement with its current wording and the artist's status; POST makes or
    withdraws one statement."""
    if request.method != "POST":
        return _statements_page(request)
    form = StatementForm(request.POST, today=timezone.localdate())
    if not form.is_valid():
        return _statements_page(
            request, form=form, error_kind=request.POST.get("kind", ""), status=400
        )
    data, artist = form.cleaned_data, _artist(request)
    if data["action"] == "withdraw":
        trust.withdraw_statement(artist, data["kind"])
        messages.success(request, _("Wycofano oświadczenie."))
        return redirect("artists:statements")
    try:
        trust.make_statement(
            artist,
            data["kind"],
            billing_form=data["billing_form"],
            valid_until=data["valid_until"],
            shown_document_id=data["document"] or 0,
        )
    except NoPublishedVersion:
        form.add_error(None, _("To oświadczenie nie jest jeszcze dostępne."))
    except StaleWording:
        form.add_error(None, _("Treść oświadczenia zmieniła się. Przeczytaj nową wersję."))
    else:
        messages.success(request, _("Zapisano oświadczenie."))
        return redirect("artists:statements")
    return _statements_page(request, form=form, error_kind=data["kind"], status=400)


# --- wizard step "Oferty" (US-2.9) -----------------------------------------------------------


class OfferForm(forms.Form):
    """Field types and limits here; the cross-field rules (price XOR "na zapytanie", age
    from <= to) come from `services.offer_errors`, the same rules the services enforce."""

    title = forms.CharField(
        label=_("Tytuł"), max_length=200, error_messages={"required": _("Podaj tytuł.")}
    )
    description = forms.CharField(
        label=_("Opis"),
        max_length=5000,
        widget=forms.Textarea,
        error_messages={"required": _("Podaj opis.")},
    )
    age_from = forms.IntegerField(
        label=_("Wiek widzów od (lat)"), min_value=0, max_value=MAX_AGE, required=False
    )
    age_to = forms.IntegerField(
        label=_("Wiek widzów do (lat)"), min_value=0, max_value=MAX_AGE, required=False
    )
    duration_minutes = forms.IntegerField(
        label=_("Czas trwania (minuty)"), min_value=1, required=False
    )
    price_pln = forms.IntegerField(label=_("Cena (zł)"), min_value=1, required=False)
    price_on_request = forms.BooleanField(label=_("Cena na zapytanie"), required=False)
    poster = forms.FileField(
        label=_("Plakat (JPG, PNG lub WebP, do 15 MB)"), required=False, allow_empty_file=True
    )
    remove_poster = forms.BooleanField(label=_("Usuń obecny plakat"), required=False)

    def clean(self):
        cleaned = super().clean()
        for field, message in services.offer_errors(cleaned).items():
            if field not in self.errors:
                self.add_error(field, message)
        return cleaned


def _offer_form_page(request, form, *, offer=None, status=200):
    context = {
        "form": form,
        "offer": offer,
        "poster_url": services.poster_url(offer) if offer else "",
    }
    return render(request, "artists/offer_form.html", context, status=status)


def _own_offer(request, offer_id):
    try:
        return services.get_offer(_artist(request), offer_id)
    except Offer.DoesNotExist as exc:
        raise Http404 from exc


@never_cache
@role_required("artist")
@_basics_required
def offers(request):
    """The artist's offers in order, with add / edit / delete / move up and down."""
    items = [(offer, services.poster_url(offer)) for offer in services.offers_for(_artist(request))]
    return render(request, "artists/offers.html", {"items": items})


def _save_offer(request, form, offer=None):
    """Call the service for a valid form; None on success, else the error page."""
    artist = _artist(request)
    data = {field: form.cleaned_data.get(field) for field in services.OFFER_FIELDS}
    poster = form.cleaned_data.get("poster") or None
    try:
        if offer is None:
            services.create_offer(artist, data, poster=poster)
        else:
            services.update_offer(
                artist,
                offer.pk,
                data,
                poster=poster,
                remove_poster=form.cleaned_data.get("remove_poster", False),
            )
    except UploadRejected as exc:
        form.add_error("poster", exc.message)
    except services.InvalidOffer as exc:  # the form uses the same rules: only on a race
        for field, message in exc.errors.items():
            form.add_error(field, message)
    else:
        return None
    return _offer_form_page(request, form, offer=offer, status=400)


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
@role_required("artist")
@_basics_required
def offer_add(request):
    if request.method != "POST":
        return _offer_form_page(request, OfferForm())
    form = OfferForm(request.POST, request.FILES)
    if not form.is_valid():
        return _offer_form_page(request, form, status=400)
    error_page = _save_offer(request, form)
    if error_page:
        return error_page
    messages.success(request, _("Dodano ofertę."))
    return redirect("artists:offers")


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
@role_required("artist")
@_basics_required
def offer_edit(request, offer_id):
    offer = _own_offer(request, offer_id)
    if request.method != "POST":
        return _offer_form_page(request, OfferForm(initial=services.offer_data(offer)), offer=offer)
    form = OfferForm(request.POST, request.FILES)
    if not form.is_valid():
        return _offer_form_page(request, form, offer=offer, status=400)
    error_page = _save_offer(request, form, offer)
    if error_page:
        return error_page
    messages.success(request, _("Zapisano ofertę."))
    return redirect("artists:offers")


@never_cache
@require_http_methods(["GET", "HEAD", "POST"])
@role_required("artist")
@_basics_required
def offer_delete(request, offer_id):
    """GET asks for confirmation, POST deletes (with the poster file)."""
    offer = _own_offer(request, offer_id)
    if request.method != "POST":
        return render(request, "artists/offer_delete.html", {"offer": offer})
    services.delete_offer(_artist(request), offer.pk)
    messages.success(request, _("Usunięto ofertę."))
    return redirect("artists:offers")


@role_required("artist")
@require_POST
@_basics_required
def offer_move(request, offer_id):
    """POST ``direction=up|down`` moves the offer one place."""
    offer = _own_offer(request, offer_id)
    direction = request.POST.get("direction")
    if direction not in ("up", "down"):
        return HttpResponseBadRequest()
    services.move_offer(_artist(request), offer.pk, direction)
    return redirect(f"{reverse('artists:offers')}#offer-{offer.pk}")
