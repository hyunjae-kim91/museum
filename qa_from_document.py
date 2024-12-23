import os
import pandas as pd
from dotenv import load_dotenv

from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain

load_dotenv()

class qaDocuments:

    def __init__(self) -> None:
        self.OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
        self.CHUNK_SIZE = 10000
        self.CHUNK_OVERLAP = 20

    def _get_chain(self):
        llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            api_key=self.OPENAI_API_KEY
        )
        return load_qa_chain(llm, chain_type="stuff", verbose=True)

    def _get_chromadb(self, document_file_name: str):
        document_path = 'src/files'
        documents_full = TextLoader(f"{document_path}/{document_file_name}", encoding="utf-8").load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.CHUNK_SIZE, chunk_overlap=self.CHUNK_OVERLAP)
        docs_full = text_splitter.split_documents(documents_full)

        embeddings = SentenceTransformerEmbeddings(model_name="jhgan/ko-sroberta-multitask")
        return Chroma.from_documents(docs_full, embeddings)

    def get_answer_from_document(self, document_file_name: str, query: str):
        chromadb = self._get_chromadb(document_file_name)
        matching_docs = chromadb.similarity_search(query)
        qa_chain = self._get_chain()
        return qa_chain.run(input_documents=matching_docs, question=query)




