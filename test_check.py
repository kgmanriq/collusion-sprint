from agent import build_agent_prompt, manipulation_check

pro_A = build_agent_prompt(trader_id=4, p_star=0.30, wording="W1")
neutral = build_agent_prompt(trader_id=2, p_star=0.30)

print("Pro-A agent says:", manipulation_check(pro_A))
print("Neutral agent says:", manipulation_check(neutral))