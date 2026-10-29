#!/usr/bin/env python3
"""Offline specification validation; does NOT test a live CS2 plugin."""
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parents[1]
c = json.loads((root/"config/vip_weapons.concept.json").read_text(encoding="utf-8"))
w = c["weapons"]
assert len(w) == 12 and len({x["id"] for x in w}) == 12
assert Counter(x["required_vip"] for x in w) == {1:4, 2:4, 3:4}
assert {x["id"] for x in w if x["slot"] == "secondary"} == {"glock18","usp_s","deagle"}
assert len({x["base_weapon"] for x in w}) == 12
assert all(x["price_snowflakes"] == {1:150,2:300,3:600}[x["required_vip"]] for x in w)
assert all(x["cooldown_seconds"] > 0 and x["trigger"] and x["result"] for x in w)
assert c["max_health"] == 110 and c["max_armor"] == 125
assert c["access_policy"]["unlock_scope"] == "current_map"
assert c["access_policy"]["nonvip_can_buy_any"]
for tier in range(4):
    free = {x["id"] for x in w if tier >= x["required_vip"]}
    assert len(free) == 4*tier, (tier, free)
print("PASS: 12 weapons, 3 pistols, 4 per tier, map access matrix and shop prices")
