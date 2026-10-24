from market import Market

m = Market(b=100) # At opening - no trades made

print("Opening price of A:", round(m.price_A(), 3))
print("Opening price of B:", round(m.price_B(), 3))

before = m.cost_function(0, 0) # Running total before trade

print("Quote for buying 10 shares of A:", round(m.quote("A", 10), 2))

m.q_A = 10 # 10 shares were bought in favor of Candidate A

print("Price of A after buying 10 shares:", round(m.price_A(), 3))
print("Price of B after buying 10 shares:", round(m.price_B(), 3))

after = m.cost_function(m.q_A,0)

print("Running total before:", round(before, 2))
print("Running total after:", round(after, 2))
print(f"Cost of buying {m.q_A} shares of A:", round(after - before, 2))

refund = m.trade("A", -10) # Refund by selling 10 shares of Candidate A
print("Refund for selling 10 shares of A:", round(refund, 2))
print("Price of A after selling 10 shares:", round(m.price_A(), 3))
print("Price of B after selling 10 shares:", round(m.price_B(), 3))

# Check that trade() charges exactly what quote() said
quoted = m.quote("A", 10)
charged = m.trade("A", 10)
print("Quoted cost of 10 A:", round(quoted, 2))
print("Charged cost of 10 A:", round(charged, 2))
print("Price of A after buying again:", round(m.price_A(), 3))

# Buy 10 shares of B
cost_B = m.trade("B", 10)
print("Cost of buying 10 shares of B:", round(cost_B, 2))
print("Price of A after buying 10 B:", round(m.price_A(), 3))
print("Price of B after buying 10 B:", round(m.price_B(), 3))
print("Prices add up to:", round(m.price_A() + m.price_B(), 3))

from agent import build_base_prompt, build_round_message

print(build_base_prompt(trader_id=2, p_star=0.10))
print("-----")
print(build_round_message(round_num=1, price_A=0.5, cash=100, shares_A=0, shares_B=0, trade_log=[]))
print("-----")
log = ["Round 1: Trader 4 bought 5 A. Trader 2 bought 3 B. Trader 1 held."]
print(build_round_message(round_num=2, price_A=0.51, cash=98.5, shares_A=0, shares_B=3, trade_log=log))