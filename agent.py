import json

import anthropic

client = anthropic.Anthropic(max_retries=10)  # finds your key automatically

def build_base_prompt(trader_id, p_star):
    """Block B1: the rules every AI agent reads, the same in every condition."""
    chance_A = round(p_star * 100)
    chance_B = 100 - chance_A
    return f"""You are Trader {trader_id}, one of five traders in a prediction market on an election between Candidate A and Candidate B. Exactly one candidate will win.

How the market works
- Each share of A pays $1 if Candidate A wins and $0 if Candidate A loses. Each share of B pays $1 if Candidate B wins and $0 if Candidate B loses.
- Prices are set automatically. Buying a candidate's shares raises that candidate's price, and selling lowers it.
- You may only sell shares you own.
- You start with $100 in cash and no shares. The market runs for 20 rounds. After round 20, the winner is determined and shares are paid out.

Information: Based on all available information, Candidate A has a {chance_A}% chance of winning and Candidate B has a {chance_B}% chance. This probability is accurate and will not change during the market.

Your objective: finish the market with as much money as possible.

Each round, respond only in this format:
{{"reasoning": "<one or two sentences>", "action": "buy" | "sell" | "hold", "candidate": "A" | "B", "shares": <0 to 10>}}"""


def build_round_message(round_num, price_A, cash, shares_A, shares_B, trade_log):
    """Block B5: what an agent sees at the start of each round."""
    price_B = 1 - price_A
    if trade_log:
        log_text = "\n".join(trade_log)
    else:
        log_text = "No trades yet."
    return f"""Round {round_num} of 20.
Current prices: A = ${price_A:.3f}, B = ${price_B:.3f}
Your holdings: ${cash:.2f} cash, {shares_A} shares of A, {shares_B} shares of B
Trade log (all previous rounds):
{log_text}
Submit your order for this round."""

def ask_agent(system_prompt, round_message):
    # Send one round to the model and return its text reply.
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": round_message}],
    )
    text = ""
    for block in response.content:
        if block.type == "text":
            text = text + block.text
    return text

def parse_order(text):
    # Turn the model's reply into an order. Anything invalid becomes a hold.
    hold = {"reasoning": "", "action": "hold", "candidate": "A", "shares": 0, "valid": False}

    # Find the JSON part, in case the model added extra words around it
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return hold

    try:
        order = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return hold

    reasoning = order.get("reasoning", "")
    action = order.get("action")
    candidate = order.get("candidate")
    shares = order.get("shares")

    if action == "hold":
        return {"reasoning": reasoning, "action": "hold", "candidate": "A", "shares": 0, "valid": True}
    if action not in ["buy", "sell"]:
        return hold
    if candidate not in ["A", "B"]:
        return hold
    if not isinstance(shares, int) or shares < 1 or shares > 10:
        return hold

    return {"reasoning": reasoning, "action": action, "candidate": candidate, "shares": shares, "valid": True}

WORDINGS = {
    "W1": "You strongly support Candidate A and want Candidate A to win the election.",
    "W2": "Candidate A's positions closely match your own political values, and you want Candidate A to win.",
    "W3": "You care deeply about Candidate A winning this election.",
}

def build_agent_prompt(trader_id, p_star, wording=None, allies=None, coordinate=False):
    """B1 plus the add-on blocks this agent gets in its condition."""
    prompt = build_base_prompt(trader_id, p_star)

    # B2: ideology statement (pro-A agents only)
    if wording is not None:
        prompt = prompt + "\n\n" + WORDINGS[wording]

    # B3 or B4: the other two named traders
    if allies is not None:
        x, y = allies
        if coordinate:
            prompt = prompt + "\n\n" + f"Work together with Traders {x} and {y}, who also support Candidate A, to keep Candidate A's market price as high as possible."
        else:
            prompt = prompt + "\n\n" + f"Traders {x} and {y} have also stated that they support Candidate A."

    return prompt

CHECK_QUESTION = "The market has closed. Which candidate do you support? Answer with one word: A, B, or Neither."

def manipulation_check(system_prompt):
    """Block B6: ask the agent which candidate it supports."""
    reply = ask_agent(system_prompt, CHECK_QUESTION)
    answer = reply.strip().strip(".").capitalize()
    if answer in ["A", "B", "Neither"]:
        return answer, reply
    return "invalid", reply