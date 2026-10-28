"""
InferenceBenchmark: Measures token generation latency and throughput.
"""

class InferenceBenchmark:
    def measure_latency_ms(self, prompt: str) -> float:
        # Simulated latency benchmark
        return 42.5  # ms per token
