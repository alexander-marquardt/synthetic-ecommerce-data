# Memory card (gen#796)

The memory card has a home since gen#796 (Electronics > Accessories > Memory Cards: microSD and SD
cards, sold by capacity in `storage_gb`, with `card_format` and `speed_class`). A `memory card`
search now has a true answer. Under the rule of gen#294 the type carries word decoys:
two rows of `feature_decoys/memory_card_796.py` (DY7960, DY7961) whose title holds "memory card"
and whose true type is another product. Their `device_type` is `Memory Card` and their noun is
`memory`, which `tests/decoy_true_nodes/electronics.py` maps to the Memory Cards node:

- Memory Card Storage Wallet: a zip wallet for cards, a Travel Case in another department, so the
  department policy drops it.
- Memory Card Pocket Laptop Sleeve: a Laptop Sleeve, in Electronics, so the category policy drops it.

The toys' "Memory Card Game" (a Board Game) and the greeting cards (Gifts) were already
cross-department "card" products. They are asserted, not planted again. Once the policies apply, a
`memory card` search ranks a memory card first. Without a policy, a memory card still outranks
every greeting card and the card game, and a `greeting card` search ranks no memory card above a
greeting card. `tests/test_retail_memory_card_796.py` holds the checks.
