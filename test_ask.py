from agent import build_base_prompt, build_round_message, ask_agent

system_prompt = build_base_prompt(trader_id=2, p_star=0.30)
round_message = build_round_message(round_num=1, price_A=0.5, cash=100, shares_A=0, shares_B=0, trade_log=[])

reply = ask_agent(system_prompt, round_message)
print(reply)