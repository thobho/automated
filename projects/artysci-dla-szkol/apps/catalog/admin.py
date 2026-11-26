"""`/django-admin/` for the dictionaries (US-4.6, D100): add, rename, deactivate, merge."""

from django import forms
from django.contrib import admin, messages
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from . import services
from .models import DictionaryEntry


class EntryAdminForm(forms.ModelForm):
    class Meta:
        model = DictionaryEntry
        fields = ("kind", "name", "is_active", "position")

    def clean_name(self):
        try:
            name = services.clean_name(self.cleaned_data["name"])
            services.check_name_free(
                self.instance, self.cleaned_data.get("kind") or self.instance.kind, name
            )
        except services.EntryError as error:
            raise forms.ValidationError(str(error)) from None
        return name


class MergeForm(forms.Form):
    target = forms.ModelChoiceField(queryset=DictionaryEntry.objects.none(), label=_("Połącz z"))

    def __init__(self, *args, source, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target"].queryset = DictionaryEntry.objects.filter(kind=source.kind).exclude(
            pk=source.pk
        )


@admin.register(DictionaryEntry)
class DictionaryEntryAdmin(admin.ModelAdmin):
    form = EntryAdminForm
    list_display = ("name", "kind", "slug", "is_active", "position", "profile_count")
    list_filter = ("kind", "is_active")
    search_fields = ("name", "slug")
    ordering = ("kind", "position", "name")
    actions = ("deactivate", "merge")

    @admin.display(description=_("profile"))
    def profile_count(self, obj):
        return services.profiles_to_move(obj)

    def get_readonly_fields(self, request, obj=None):
        return ("kind", "slug") if obj else ()

    def get_form(self, request, obj=None, **kwargs):
        if obj:  # kind is read-only after creation
            kwargs["fields"] = ("name", "is_active", "position")
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        # The slug is made once, here, from the name (the service owns the rule) and never changes.
        if not change:
            obj.slug = services.slug_for(obj.kind, obj.name)
        obj.save()

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.assignments.exists():
            return False
        return super().has_delete_permission(request, obj)

    @admin.action(description=_("Dezaktywuj zaznaczone pozycje"), permissions=["change"])
    def deactivate(self, request, queryset):
        for entry in queryset:
            services.deactivate_entry(entry)
        self.message_user(request, _("Dezaktywowano pozycje: %d.") % queryset.count())

    @admin.action(description=_("Połącz z inną pozycją"), permissions=["change"])
    def merge(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, _("Zaznacz dokładnie jedną pozycję."), messages.ERROR)
            return None
        source = queryset.get()
        if "apply" in request.POST:
            form = MergeForm(request.POST, source=source)
            if form.is_valid():
                target = form.cleaned_data["target"]
                try:
                    moved = services.merge_entries(source, target)
                except services.EntryError as error:
                    self.message_user(request, str(error), messages.ERROR)
                    return None
                self.message_user(
                    request,
                    _("Połączono „%(source)s” z „%(target)s”; przeniesiono profile: %(count)d.")
                    % {"source": source.name, "target": target.name, "count": moved},
                )
                return None
        else:
            form = MergeForm(source=source)
        context = {
            **self.admin_site.each_context(request),
            "title": _("Połącz pozycję z inną"),
            "opts": self.model._meta,
            "source": source,
            "count": services.profiles_to_move(source),
            "form": form,
            "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
        }
        return TemplateResponse(request, "catalog/merge_entries.html", context)
