from market import Market
from agent import build_agent_prompt
from trading import Trader, run_round

m = Market(b=100)
traders = [
    Trader(1, build_agent_prompt(1, 0.30, wording="W1", allies=(3, 5))),
    Trader(2, build_agent_prompt(2, 0.30)),
    Trader(3, build_agent_prompt(3, 0.30, wording="W1", allies=(1, 5))),
    Trader(4, build_agent_prompt(4, 0.30)),
    Trader(5, build_agent_prompt(5, 0.30, wording="W1", allies=(1, 3))),
]
trade_log = []

for round_num in [1, 2]:
    records = run_round(m, traders, round_num, trade_log)
    print(trade_log[-1])
    print("Price of A:", round(m.price_A(), 3))
    for r in records:
        print("  Trader", r["trader"], "->", r["reasoning"])