"""The carry bags family of the line grammar: belt, messenger and laptop bags (gen#1114, gen#513).

A family of its own, so the models of :mod:`bags` keep their names. A model is a plain word of the
working town and an optional sub-model, then the descriptors and the kind, the brand first ("Brand
Concourse Canvas Courier Messenger Bag"). It carries no number: on a bag a number reads as a size
or a screen size. The lead words are plain English words no other template's text uses, so no lead
leaves another family's deal.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = ("Belt Bag", "Messenger Bag", "Laptop Bag")
#: The lead word of a model.
LEADS = (
    "Concourse", "Turnpike", "Cloister", "Chancery", "Embassy", "Tribune", "Dispatch", "Terminus",
    "Viaduct", "Thoroughfare", "Bureau", "Envoy", "Consul", "Syndicate", "Precinct", "Guildhall",
    "Tramway", "Causeway", "Borough", "Exchange", "Parkway", "Forum",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Duo", "Lux")
#: No generation number (see the module doc).
NUMBERS = ()
