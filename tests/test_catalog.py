#!/usr/bin/env python3
"""Offline configuration checks only; not proof of working CS2 mechanics."""
import json
from collections import Counter
from pathlib import Path
r = Path(__file__).resolve().parents[1]
d = json.loads((r / "config/vip_weapons.concept.json").read_text(encoding="utf-8"))
w = d["weapons"]
assert len(w) == 12
assert len({x["id"] for x in w}) == 12
assert len({x["base_weapon"] for x in w}) == 12
assert Counter(x["required_vip"] for x in w) == {1:4,2:4,3:4}
assert {x["id"] for x in w if x["slot"] == "secondary"} == {"glock18","usp_s","deagle"}
assert all(x["status"] == "concept_not_game_tested" for x in w)
assert all(x["name"] and x["ability"] and x["trigger"] and x["cooldown"] for x in w)
assert [d["vip_finishes"][x]["cycle_seconds"] for x in ("VIP_I","VIP_II","VIP_III")] == [5,3.5,4]
assert d["max_health"] == 110 and d["max_armor"] == 125
rule = d["default_grant_behavior"]
assert rule["when"] == "immediately_in_current_life"
assert rule["respawn_required"] is False and rule["equip"] is True
assert rule["refund_on_failure"] is True and rule["charge_only_after_success"] is True
assert rule["allow_pickup"] is False
print("PASS: 12 weapons, 3 pistols, VIP finishes, instant-grant contract, HP/armor limits")
