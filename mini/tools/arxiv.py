import os
from langchain_community.retrievers import ArxivRetriever

class Arxiv:
    def __init__(self):
        self.retriever = ArxivRetriever(
            # load_max_docs=2,
            top_k_results=5,
            get_ful_documents=True,
        )

    def search(self, query):
        result = self.retriever.get_relevant_documents(query)

        context = ""
        for r in result:
            context+= f"Title: {r.metadata['Title']}\n"
            context+= f"Authors: {r.metadata['Authors']}\n"
            context+= f"Link: {r.metadata['Entry ID']}\n"
            context+= f"Content: {r.page_content}\n\n"

        return context