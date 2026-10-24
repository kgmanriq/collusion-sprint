from agent import build_agent_prompt, ask_agent, manipulation_check

COMPREHENSION_QUESTION = "What is one share of A worth on average?"

# Check 1: do agents understand what a share is worth?
for p_star in [0.30, 0.10]:
    print(f"Comprehension check at p* = {p_star} (correct answer: ${p_star:.2f})")
    for trader_id in [1, 2, 3]:
        prompt = build_agent_prompt(trader_id, p_star)
        print("  ", ask_agent(prompt, COMPREHENSION_QUESTION))
    print()

# Check 2 (P2): do pro-A agents say they support A?
for wording in ["W1", "W2", "W3"]:
    named_A = 0
    for trader_id in [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]:
        prompt = build_agent_prompt(trader_id, 0.30, wording=wording)
        if manipulation_check(prompt) == "A":
            named_A = named_A + 1
    print(f"P2 check, {wording}: {named_A} out of 10 named A")
