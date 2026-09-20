        """Minimal WaveSpeed example: create one prediction and print the output URL(s)."""
        import wavespeed_api

        output = wavespeed_api.run({
    "prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light"
})
        print(output)
