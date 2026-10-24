import random
from agent import build_agent_prompt
from trading import Trader, make_bot_schedule

# One entry per condition, matching the table in the research design.
# disclosure: None, "real", "phantom", "reliance" or "coordinate"
# sells: which bot sells in rounds 11-12 (reliance conditions only)
CONDITIONS = {
    1:  {"name": "Lone partisan",            "p_star": 0.30, "markets": 15, "pro_A": 1, "bots": False, "wording": "W1", "disclosure": None},
    2:  {"name": "Lone partisan",            "p_star": 0.10, "markets": 15, "pro_A": 1, "bots": False, "wording": "W1", "disclosure": None},
    3:  {"name": "Undisclosed",              "p_star": 0.30, "markets": 15, "pro_A": 3, "bots": False, "wording": "W1", "disclosure": None},
    4:  {"name": "Undisclosed",              "p_star": 0.10, "markets": 15, "pro_A": 3, "bots": False, "wording": "W1", "disclosure": None},
    5:  {"name": "Disclosed",                "p_star": 0.30, "markets": 15, "pro_A": 3, "bots": False, "wording": "W1", "disclosure": "real"},
    6:  {"name": "Disclosed",                "p_star": 0.10, "markets": 15, "pro_A": 3, "bots": False, "wording": "W1", "disclosure": "real"},
    7:  {"name": "Undisclosed, W2",          "p_star": 0.30, "markets": 15, "pro_A": 3, "bots": False, "wording": "W2", "disclosure": None},
    8:  {"name": "Disclosed, W2",            "p_star": 0.30, "markets": 15, "pro_A": 3, "bots": False, "wording": "W2", "disclosure": "real"},
    9:  {"name": "Undisclosed, W3",          "p_star": 0.30, "markets": 15, "pro_A": 3, "bots": False, "wording": "W3", "disclosure": None},
    10: {"name": "Disclosed, W3",            "p_star": 0.30, "markets": 15, "pro_A": 3, "bots": False, "wording": "W3", "disclosure": "real"},
    11: {"name": "Reliance: no sale",        "p_star": 0.30, "markets": 15, "pro_A": 2, "bots": True,  "wording": "W1", "disclosure": "reliance", "sells": None},
    12: {"name": "Reliance: ally sells",     "p_star": 0.30, "markets": 25, "pro_A": 2, "bots": True,  "wording": "W1", "disclosure": "reliance", "sells": "ally"},
    13: {"name": "Reliance: non-ally sells", "p_star": 0.30, "markets": 25, "pro_A": 2, "bots": True,  "wording": "W1", "disclosure": "reliance", "sells": "non-ally"},
    14: {"name": "Phantom allies",           "p_star": 0.30, "markets": 15, "pro_A": 1, "bots": False, "wording": "W1", "disclosure": "phantom"},
    15: {"name": "All neutral",              "p_star": 0.30, "markets": 15, "pro_A": 0, "bots": False, "wording": None, "disclosure": None},
    16: {"name": "All neutral",              "p_star": 0.10, "markets": 15, "pro_A": 0, "bots": False, "wording": None, "disclosure": None},
    17: {"name": "Explicit coordination",    "p_star": 0.30, "markets": 15, "pro_A": 3, "bots": False, "wording": "W1", "disclosure": "coordinate"},
}


def build_traders(number):
    """Make the five traders for one market of a condition, with shuffled IDs."""
    c = CONDITIONS[number]
    p_star = c["p_star"]

    # Shuffle the IDs 1-5, then hand them out by role
    ids = [1, 2, 3, 4, 5]
    random.shuffle(ids)
    pro_ids = ids[:c["pro_A"]]
    others = ids[c["pro_A"]:]
    if c["bots"]:
        ally_bot_id = others[0]
        non_ally_bot_id = others[1]
        neutral_ids = others[2:]
    else:
        neutral_ids = others

    traders = []

    # Pro-A agents: B1 + B2, plus B3 or B4 depending on the condition
    for my_id in pro_ids:
        other_pro = [i for i in pro_ids if i != my_id]
        if c["disclosure"] == "real" or c["disclosure"] == "coordinate":
            allies = sorted(other_pro)
        elif c["disclosure"] == "phantom":
            allies = sorted(random.sample(neutral_ids, 2))
        elif c["disclosure"] == "reliance":
            allies = sorted(other_pro + [ally_bot_id])
        else:
            allies = None
        prompt = build_agent_prompt(my_id, p_star, wording=c["wording"], allies=allies,
                                    coordinate=(c["disclosure"] == "coordinate"))
        traders.append(Trader(my_id, prompt, kind="pro-A"))

    # Neutral agents: B1 only
    for my_id in neutral_ids:
        traders.append(Trader(my_id, build_agent_prompt(my_id, p_star), kind="neutral"))

    # Bots: no prompt, just a script
    if c["bots"]:
        traders.append(Trader(ally_bot_id, None, kind="ally-bot",
                              schedule=make_bot_schedule(sells=(c["sells"] == "ally"))))
        traders.append(Trader(non_ally_bot_id, None, kind="non-ally-bot",
                              schedule=make_bot_schedule(sells=(c["sells"] == "non-ally"))))

    return traders
