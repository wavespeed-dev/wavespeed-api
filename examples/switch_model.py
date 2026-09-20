"""The same client drives every hosted model listed in wavespeed_api.MODELS."""
from wavespeed_api import Client, MODELS

client = Client()
for slug, info in MODELS.items():
    print(slug, "->", info["category"], "required:", info["required"])
# pick one explicitly
output = client.run({"prompt": "A woman is talking", "input_image": "https://example.com/input.png"}, model="tongyi/wan2.2")
print(output)
