from market import Market
from trading import Trader, execute_order

m = Market(b=100)
t = Trader(trader_id=3, prompt="(prompt goes here)")

print(execute_order(m, t, {"action": "buy", "candidate": "B", "shares": 10}))
print("Cash:", round(t.cash, 2), "| B shares:", t.shares_B, "| Price of A:", round(m.price_A(), 3))

print(execute_order(m, t, {"action": "sell", "candidate": "A", "shares": 5}))
print(execute_order(m, t, {"action": "sell", "candidate": "B", "shares": 4}))
print("Cash:", round(t.cash, 2), "| B shares:", t.shares_B)

t.cash = 2.0
print(execute_order(m, t, {"action": "buy", "candidate": "A", "shares": 10}))
print(execute_order(m, t, {"action": "hold", "candidate": "A", "shares": 0}))