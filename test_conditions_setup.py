from conditions import CONDITIONS, build_traders

for number in [1, 5, 12, 14, 17]:
    print(f"Condition {number}: {CONDITIONS[number]['name']}")
    for t in build_traders(number):
        if t.prompt is None:
            last_line = "(bot, no prompt)"
        else:
            last_line = t.prompt.split("\n")[-1]
        print(f"  Trader {t.id} ({t.kind}): {last_line}")
    print()
