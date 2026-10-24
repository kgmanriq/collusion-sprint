from agent import build_agent_prompt

print(build_agent_prompt(trader_id=4, p_star=0.30))
print("-----")
print(build_agent_prompt(trader_id=4, p_star=0.30, wording="W1"))
print("-----")
print(build_agent_prompt(trader_id=4, p_star=0.30, wording="W1", allies=(1, 5)))
print("-----")
print(build_agent_prompt(trader_id=4, p_star=0.30, wording="W1", allies=(1, 5), coordinate=True))