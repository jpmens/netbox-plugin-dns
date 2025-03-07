from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel
from netbox.search import SearchIndex, register_search
from netbox.models.features import ContactsMixin

from netbox_dns.choices import DNSSECPolicyDigestChoices
from netbox_dns.fields import ChoiceArrayField


__all__ = (
    "DNSSECPolicy",
    "DNSSECPolicyIndex",
)


class DNSSECPolicy(ContactsMixin, NetBoxModel):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        unique=True,
    )
    description = models.CharField(
        verbose_name=_("Description"),
        max_length=200,
        blank=True,
    )

    key_templates = models.ManyToManyField(
        verbose_name=_("Key Templates"),
        to="DNSSECKeyTemplate",
        related_name="policies",
        blank=True,
    )
    dnskey_ttl = models.PositiveIntegerField(
        verbose_name=_("DNSKEY TTL"),
        blank=True,
        null=True,
    )
    purge_keys = models.PositiveIntegerField(
        verbose_name=_("Purge Keys"),
        blank=True,
        null=True,
    )
    publish_safety = models.PositiveIntegerField(
        verbose_name=_("Publish Safety"),
        blank=True,
        null=True,
    )
    retire_safety = models.PositiveIntegerField(
        verbose_name=_("Retire Safety"),
        blank=True,
        null=True,
    )
    signatures_jitter = models.PositiveIntegerField(
        verbose_name=_("Signatures Jitter"),
        blank=True,
        null=True,
    )
    signatures_refresh = models.PositiveIntegerField(
        verbose_name=_("Signatures Refresh"),
        blank=True,
        null=True,
    )
    signatures_validity = models.PositiveIntegerField(
        verbose_name=_("Signatures Validity"),
        blank=True,
        null=True,
    )
    signatures_validity_dnskey = models.PositiveIntegerField(
        verbose_name=_("Signatures Validity for DNSKEY"),
        blank=True,
        null=True,
    )
    max_zone_ttl = models.PositiveIntegerField(
        verbose_name=_("Max Zone TTL"),
        blank=True,
        null=True,
    )
    zone_propagation_delay = models.PositiveIntegerField(
        verbose_name=_("Zone Propagation Delay"),
        blank=True,
        null=True,
    )

    create_cdnskey = models.BooleanField(
        verbose_name=_("Create CDNSKEY"),
        null=False,
        default=True,
    )
    cds_digest_types = ChoiceArrayField(
        base_field=models.CharField(
            choices=DNSSECPolicyDigestChoices,
        ),
        verbose_name=_("CDS Digest Types"),
        blank=True,
        null=True,
        default=list,
    )
    parent_ds_ttl = models.PositiveIntegerField(
        verbose_name=_("Parent DS TTL"),
        blank=True,
        null=True,
    )
    parent_propagation_delay = models.PositiveIntegerField(
        verbose_name=_("Parent Propagation Delay"),
        blank=True,
        null=True,
    )

    use_nsec3 = models.BooleanField(
        verbose_name=_("Use NSEC3"),
        null=False,
        default=True,
    )
    nsec3_iterations = models.PositiveIntegerField(
        verbose_name=_("NSEC3 Iterations"),
        blank=True,
        null=True,
    )
    nsec3_opt_out = models.BooleanField(
        verbose_name=_("NSEC3 Opt-Out"),
        blank=False,
        null=False,
        default=False,
    )
    nsec3_salt_size = models.PositiveIntegerField(
        verbose_name=_("NSEC3 Salt Size"),
        blank=True,
        null=True,
    )

    tenant = models.ForeignKey(
        verbose_name=_("Tenant"),
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="netbox_dns_dnssec_policy",
        blank=True,
        null=True,
    )

    clone_fields = (
        "name",
        "description",
        "tenant",
    )

    class Meta:
        verbose_name = _("DNSSEC Policy")
        verbose_name_plural = _("DNSSEC Policies")

        ordering = ("name",)

    def __str__(self):
        return str(self.name)

    # TODO: Remove in version 1.3.0 (NetBox #18555)
    def get_absolute_url(self):
        return reverse("plugins:netbox_dns:dnssecpolicy", kwargs={"pk": self.pk})


@register_search
class DNSSECPolicyIndex(SearchIndex):
    model = DNSSECPolicy
    fields = (
        ("name", 100),
        ("description", 500),
    )
