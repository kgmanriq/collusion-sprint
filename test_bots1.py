from market import Market
from trading import Trader, make_bot_schedule, run_round

m = Market(b=300)
bots = [
    Trader(2, None, kind="ally-bot", schedule=make_bot_schedule(sells=True)),
    Trader(4, None, kind="non-ally-bot", schedule=make_bot_schedule(sells=False)),
]
trade_log = []

for round_num in range(1, 17):
    run_round(m, bots, round_num, trade_log)
    print(trade_log[-1], "| Price of A:", round(m.price_A(), 3))

for bot in bots:
    print(f"Trader {bot.id} ({bot.kind}): {bot.shares_A} shares of A, ${bot.cash:.2f} cash")
