import anthropic

client = anthropic.Anthropic()  # finds your key automatically

response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Reply with only the word: ready"}],
)

for block in response.content:
    if block.type == "text":
        print(block.text)

print(response.usage)  # how many tokens you used, which is what you pay for
