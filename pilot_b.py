from conditions import CONDITIONS, build_traders
from trading import run_market

summary = []

for b in [200, 300, 500]:
    # Two all-neutral markets at p* = 0.30 (condition 15), one at p* = 0.10 (condition 16)
    for i, number in enumerate([15, 15, 16]):
        p_star = CONDITIONS[number]["p_star"]
        traders = build_traders(number)
        data = run_market(traders, p_star=p_star, b=b, market_name=f"pilot_b{b}_{i + 1}")
        last_five = data["price_history"][15:20]   # rounds 16-20
        average = sum(last_five) / len(last_five)
        gap = average - p_star
        bounce = max(last_five) - min(last_five)
        line = (f"b = {b}, p* = {p_star}: average price of A in rounds 16-20 = {average:.3f}, "
                f"gap from p* = {gap:+.3f}, bounce = {bounce:.3f}")
        print(line)
        summary.append(line)

        # Save the summary so far, so nothing is lost if the run stops early
        with open("results/pilot_b_summary.txt", "w") as f:
            f.write("\n".join(summary) + "\n")

print()
print("Done. Summary:")
for line in summary:
    print(line)
