import dns
from dns import name as dns_name

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search
from netbox.plugins.utils import get_plugin_config

from netbox_dns.validators import validate_generic_name, validate_record_value

from netbox_dns.choices import RecordTypeChoices, RecordStatusChoices


__ALL__ = (
    "RecordTemplate",
    "RecordTemplateIndex",
)


class RecordTemplate(NetBoxModel):
    name = models.CharField(
        verbose_name="Template name",
        unique=True,
        max_length=200,
    )
    record_name = models.CharField(
        verbose_name="Name",
        max_length=255,
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    type = models.CharField(
        choices=RecordTypeChoices,
    )
    value = models.CharField(
        max_length=65535,
    )
    status = models.CharField(
        choices=RecordStatusChoices,
        default=RecordStatusChoices.STATUS_ACTIVE,
        blank=False,
    )
    ttl = models.PositiveIntegerField(
        verbose_name="TTL",
        null=True,
        blank=True,
    )
    disable_ptr = models.BooleanField(
        verbose_name="Disable PTR",
        help_text="Disable PTR record creation",
        default=False,
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="+",
        blank=True,
        null=True,
    )

    clone_fields = [
        "record_name",
        "description",
        "type",
        "value",
        "status",
        "ttl",
        "disable_ptr",
        "tenant",
    ]

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return str(self.name)

    def get_status_color(self):
        return RecordStatusChoices.colors.get(self.status)

    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:recordtemplate", kwargs={"pk": self.pk})

    def validate_name(self):
        try:
            name = dns_name.from_text(self.record_name, origin=None)
            name.to_unicode()

        except dns.exception.DNSException as exc:
            raise ValidationError({"record_name": str(exc)})

        if self.type not in get_plugin_config(
            "netbox_dns", "tolerate_non_rfc1035_types", default=[]
        ):
            try:
                validate_generic_name(
                    self.record_name,
                    (
                        self.type
                        in get_plugin_config(
                            "netbox_dns",
                            "tolerate_leading_underscore_types",
                            default=[],
                        )
                    ),
                )
            except ValidationError as exc:
                raise ValidationError(
                    {
                        "record_name": exc,
                    }
                ) from None

    def validate_value(self):
        try:
            validate_record_value(self.type, self.value)
        except ValidationError as exc:
            raise ValidationError({"value": exc}) from None

    def clean_fields(self, *args, **kwargs):
        self.type = self.type.upper()
        super().clean_fields(*args, **kwargs)

    def clean(self, *args, **kwargs):
        self.validate_name()
        self.validate_value()

        super().clean(*args, **kwargs)


@register_search
class RecordTemplateIndex(SearchIndex):
    model = RecordTemplate
    fields = (
        ("name", 100),
        ("record_name", 120),
        ("value", 150),
        ("type", 200),
    )
