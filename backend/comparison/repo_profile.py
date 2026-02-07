class RepoProfile:
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm

    def build(self, repo_namespace: str) -> str:
        """
        Build a concise technical profile of a repository
        using already-ingested embeddings.
        """

        # IMPORTANT:
        # Your retriever_new.retrieve() DOES NOT accept `namespace=`
        # It filters internally using metadata.repo_url
        context_chunks = self.retriever.retrieve(
            query="Describe the tech stack, architecture, and purpose of this repository",
            repo_url=repo_namespace
        )

        prompt = f"""
You are analyzing a GitHub repository.

Based ONLY on the context below, produce:
1. A 3–5 line concise summary
2. Tech stack
3. Architectural approach
4. Intended use cases

Context:
{context_chunks}
"""

        return self.llm.generate(prompt)
