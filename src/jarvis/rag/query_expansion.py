from langchain_google_genai import ChatGoogleGenerativeAI

from jarvis.rag.base import RAGStep
from jarvis.domain.queries import Query
from jarvis.rag.prompt_templates import QueryExpansionTemplate


class QueryExpansion(RAGStep):

    def generate(self, query, expand_to_n: int) -> list[Query]:
        assert (
            expand_to_n > 0
        ), f"'expand_to_n' must be greater than 0, got {expand_to_n}."

        if self._mock:
            return [query for _ in range(expand_to_n)]

        query_expansion_template = QueryExpansionTemplate()
        prompt = query_expansion_template.create_template(expand_to_n - 1)
        model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

        chain = prompt | model

        response = chain.invoke({"question": query})
        result = response.content

        queries_content = result.strip().split(query_expansion_template.separator)

        queries = [query]
        queries += [
            query.replace_content(stripped_content)
            for content in queries_content
            if (stripped_content := content.strip())
        ]

        return queries


if __name__ == "__main__":
    qe = Query.from_str("How can I structure a RAG system?")
    expanded_queries = QueryExpansion().generate(qe, 4)
    for expanded_query in expanded_queries:
        print(expanded_query.content)
