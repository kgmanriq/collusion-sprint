import os
import time
from conditions import CONDITIONS, build_traders
from trading import run_market

B = 300   # chosen in pilot step 6b

# All 17 conditions are interleaved from the start, as the pre-registration states.
ALL_CONDITIONS = list(range(1, 18))


def market_plan(group):
    """Interleave conditions: market 1 of each, then market 2 of each, and so on."""
    plan = []
    most = max(CONDITIONS[number]["markets"] for number in group)
    for i in range(1, most + 1):
        for number in group:
            if i <= CONDITIONS[number]["markets"]:
                plan.append((number, i))
    return plan


plan = market_plan(ALL_CONDITIONS)
os.makedirs("results/main", exist_ok=True)
failures_in_a_row = 0

for count, (number, i) in enumerate(plan, start=1):
    name = f"main/c{number:02d}_m{i:02d}"

    # Skip markets that already finished, so the script can pick up where it left off
    if os.path.exists(f"results/{name}.json"):
        continue

    print(f"[{count}/{len(plan)}] Condition {number} ({CONDITIONS[number]['name']}), market {i}")
    start = time.time()
    try:
        traders = build_traders(number)
        run_market(traders, CONDITIONS[number]["p_star"], B, name, condition=number)
    except Exception as error:
        print(f"  Failed: {error}")
        print("  This market was not saved and will be rerun next time you start the script.")
        failures_in_a_row = failures_in_a_row + 1
        if failures_in_a_row >= 3:
            print("Stopping after 3 failures in a row. Check the error above before restarting.")
            break
        continue

    failures_in_a_row = 0
    print(f"  Done in {time.time() - start:.0f} seconds")

print("Finished this run.")
