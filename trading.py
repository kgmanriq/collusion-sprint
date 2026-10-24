import random
from concurrent.futures import ThreadPoolExecutor
import json
import os
from market import Market
from agent import build_round_message, ask_agent, parse_order, manipulation_check


class Trader:
    """One trader's account: its ID, its prompt, and what it owns."""

    def __init__(self, trader_id, prompt, kind="neutral", schedule=None):
        self.id = trader_id
        self.prompt = prompt
        self.kind = kind
        self.schedule = schedule
        self.cash = 100.0
        self.shares_A = 0
        self.shares_B = 0

    def shares_of(self, candidate):
        if candidate == "A":
            return self.shares_A
        else:
            return self.shares_B

    def add_shares(self, candidate, shares):
        if candidate == "A":
            self.shares_A = self.shares_A + shares
        else:
            self.shares_B = self.shares_B + shares


HOLD = {"reasoning": "", "action": "hold", "candidate": "A", "shares": 0, "valid": True}


# Bot settings, chosen in pilot step 6c for b = 300
BOT_BUY_PER_ROUND = 5                  # rounds 1-10: buy 5 A each round (50 shares in total)
BOT_SELL_ROUNDS = [11, 12, 13, 14, 15]  # the selling bot sells 10 A in each of these rounds
BOT_SELL_PER_ROUND = 10


def make_bot_schedule(sells):
    """The bot's fixed orders for each round.
    Rounds 1-10: buy BOT_BUY_PER_ROUND A. Then, only if sells is True,
    sell BOT_SELL_PER_ROUND A in each of BOT_SELL_ROUNDS. Any round not listed is a hold."""
    schedule = {}
    for round_num in range(1, 11):
        schedule[round_num] = {"reasoning": "bot", "action": "buy", "candidate": "A", "shares": BOT_BUY_PER_ROUND, "valid": True}
    if sells:
        for round_num in BOT_SELL_ROUNDS:
            schedule[round_num] = {"reasoning": "bot", "action": "sell", "candidate": "A", "shares": BOT_SELL_PER_ROUND, "valid": True}
    return schedule


def execute_order(market, trader, order):
    """Carry out one order if the trader can afford it or owns the shares.
    Returns the line for the trade log and whether the order went through."""
    action = order["action"]
    candidate = order["candidate"]
    shares = order["shares"]

    if action == "buy":
        cost = market.quote(candidate, shares)
        if cost > trader.cash:
            return f"Trader {trader.id} held.", False
        market.trade(candidate, shares)
        trader.cash = trader.cash - cost
        trader.add_shares(candidate, shares)
        return f"Trader {trader.id} bought {shares} {candidate}.", True

    if action == "sell":
        if shares > trader.shares_of(candidate):
            return f"Trader {trader.id} held.", False
        refund = -market.trade(candidate, -shares)
        trader.cash = trader.cash + refund
        trader.add_shares(candidate, -shares)
        return f"Trader {trader.id} sold {shares} {candidate}.", True

    return f"Trader {trader.id} held.", True


def decide(trader, round_num, price_A, trade_log):
    """One trader's order for this round: from its script if it's a bot, otherwise from the model."""
    if trader.schedule is not None:
        return trader, trader.schedule.get(round_num, HOLD), "(bot)", None
    message = build_round_message(round_num, price_A, trader.cash, trader.shares_A, trader.shares_B, trade_log)
    reply = ask_agent(trader.prompt, message)
    return trader, parse_order(reply), reply, message


def run_round(market, traders, round_num, trade_log):
    """One round: every trader decides from the same prices,
    then the orders are carried out in a shuffled order."""
    price_A = market.price_A()

    # Step 1: everyone decides at the same time, seeing the same start-of-round market
    with ThreadPoolExecutor(max_workers=len(traders)) as pool:
        jobs = [pool.submit(decide, trader, round_num, price_A, trade_log) for trader in traders]
        decisions = [job.result() for job in jobs]

    # Step 2: carry out the orders in a random order
    random.shuffle(decisions)
    log_lines = []
    records = []
    for trader, order, reply, message in decisions:
        line, executed = execute_order(market, trader, order)
        log_lines.append(line)
        records.append({
            "round": round_num,
            "trader": trader.id,
            "reasoning": order["reasoning"],
            "action": order["action"],
            "candidate": order["candidate"],
            "shares": order["shares"],
            "valid": order["valid"],
            "executed": executed,
            "price_A_after": market.price_A(),
            "round_message": message,
            "raw_reply": reply,
        })

    # Step 3: add this round to the trade log everyone sees next round
    trade_log.append(f"Round {round_num}: " + " ".join(log_lines))
    return records


def run_market(traders, p_star, b, market_name, condition=None):
    """One full market: 20 rounds, then the manipulation check, then save everything."""
    market = Market(b)
    trade_log = []
    all_records = []
    price_history = []

    for round_num in range(1, 21):
        records = run_round(market, traders, round_num, trade_log)
        all_records = all_records + records
        price_history.append(market.price_A())
        print(f"Round {round_num} done. Price of A: {market.price_A():.3f}")

    # Draw the winner using the true probability
    a_wins = random.random() < p_star

    trader_results = []
    for trader in traders:
        expected_wealth = trader.cash + trader.shares_A * p_star + trader.shares_B * (1 - p_star)
        if a_wins:
            final_money = trader.cash + trader.shares_A
        else:
            final_money = trader.cash + trader.shares_B
        if trader.schedule is None:
            support, support_reply = manipulation_check(trader.prompt)
        else:
            support, support_reply = "bot", None
        trader_results.append({
            "trader": trader.id,
            "kind": trader.kind,
            "cash": trader.cash,
            "shares_A": trader.shares_A,
            "shares_B": trader.shares_B,
            "expected_wealth": expected_wealth,
            "final_money": final_money,
            "support": support,
            "support_reply": support_reply,
            "prompt": trader.prompt,
        })

    data = {
        "market": market_name,
        "condition": condition,
        "p_star": p_star,
        "b": b,
        "a_wins": a_wins,
        "final_price_A": market.price_A(),
        "price_history": price_history,
        "trade_log": trade_log,
        "traders": trader_results,
        "records": all_records,
    }

    os.makedirs("results", exist_ok=True)
    with open(f"results/{market_name}.json", "w") as f:
        json.dump(data, f, indent=2)

    return data
