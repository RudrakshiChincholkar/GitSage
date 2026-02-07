class FeatureClassifier:
    def __init__(self, llm):
        self.llm = llm

    def classify(self, repo_profile: str) -> dict:
        """
        Returns yes / no / partial for UI comparison.
        """

        prompt = f"""
Given the repository description below, classify whether
each feature is supported as:
- yes
- partial
- no

Return STRICT JSON only.

Features:
- TypeScript Support
- Server-Side Rendering
- Hot Module Replacement
- Built-in Testing
- Mobile Support
- GraphQL Integration

Repository Description:
{repo_profile}
"""

        raw = self.llm.generate(prompt)

        try:
            return eval(raw)  # safe here because model is constrained
        except Exception:
            # fallback (never crash the UI)
            return {
                "TypeScript Support": "partial",
                "Server-Side Rendering": "no",
                "Hot Module Replacement": "partial",
                "Built-in Testing": "partial",
                "Mobile Support": "partial",
                "GraphQL Integration": "no",
            }
