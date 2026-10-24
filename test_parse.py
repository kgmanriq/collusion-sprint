from agent import parse_order

good = '{"reasoning": "B is underpriced.", "action": "buy", "candidate": "B", "shares": 10}'
chatty = 'Here is my order: {"reasoning": "Hold for now.", "action": "hold", "candidate": "A", "shares": 0} Thanks!'
too_many = '{"reasoning": "All in.", "action": "buy", "candidate": "B", "shares": 50}'
broken = 'I think I will buy B'

print(parse_order(good))
print(parse_order(chatty))
print(parse_order(too_many))
print(parse_order(broken))