import json
import os
import requests

os.environ["AZURESEARCH_FIELDS_ID"] = "doc_id"
os.environ["AZURESEARCH_FIELDS_METADATA"] = "title"
os.environ["AZURESEARCH_FIELDS_CONTENT_VECTOR"] = "vectorContent"
os.environ["AZURESEARCH_FIELDS_CONTENT"] = "textContent"

from langchain.vectorstores.azuresearch import AzureSearch
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from typing import Tuple

# pylint: disable=import-error
from .callbacks import ThoughtsCallbackHandler
from langchain.retrievers import AzureCognitiveSearchRetriever

load_dotenv()


class Configuration:
    """A class used to manage Configuration"""

    def __init__(self, config_file: str) -> None:
        self.load_environment()
        self.config = self.load_config_file(config_file)
        self.api = self.load_api_configuration()

    def load_environment(self) -> None:
        load_dotenv()

    def load_config_file(self, config_file: str) -> dict:
        with open(config_file, "r") as f:
            return json.load(f)

    def load_api_configuration(self) -> dict:
        return {
            "api_key": os.getenv("API_KEY"),
            # "api_base": os.getenv("API_BASE"),
            # "deployment_name": os.getenv("DEPLOYMENT_NAME"),
            # "embedding_name": os.getenv("EMBEDDING_NAME"),
            "api_type": "openai",
            "api_version": "2023-05-15",
            "data_context": self.config["DATA"]["CONTEXT"],
        }


class VectorStoreManagement:
    """A class used to manage vector store operations"""

    def __init__(self, embeddings: OpenAIEmbeddings, config: Configuration) -> None:
        self.vector_store = azure_search_init(config, embeddings)
        self.azure = AzureCognitiveSearchRetriever(content_key="content", top_k=10)
        self.retriever = self.vector_store.as_retriever()


class ChatOpenAIManagement:
    """A class used to manage ChatOpenAI operations"""

    def __init__(
        self,
        # deployment_name: str,
        # api_base: str,
        # api_version: str,
        api_key: str,
        # api_type: str,
    ):
        self.llm = ChatOpenAI(
            temperature=0.1,
            # deployment_name=deployment_name,
            model="gpt-3.5-turbo",
            # openai_api_base=api_base,
            # openai_api_version=api_version,
            openai_api_key=api_key,
            # openai_api_type=api_type,
        )
        self.condense_question_prompt = PromptTemplate.from_template(
            """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

                Chat History:
                {chat_history}
                Follow Up Input: {question}
                Standalone question:"""
        )

    def create_qa(
        self, retriever, combine_docs_chain_kwargs
    ) -> ConversationalRetrievalChain:
        return ConversationalRetrievalChain.from_llm(
            self.llm,
            retriever=retriever,
            condense_question_prompt=self.condense_question_prompt,
            combine_docs_chain_kwargs=combine_docs_chain_kwargs,
            return_source_documents=True,
            return_generated_question=True,
        )

    def execute(
        self,
        question: str,
        memory: ConversationBufferMemory,
        handler: ThoughtsCallbackHandler,
        qa: ConversationalRetrievalChain,
    ) -> dict:
        inputs = {
            "question": question,
            "chat_history": memory.load_memory_variables({})["chat_history"],
        }
        result = qa(inputs, callbacks=[handler])
        memory.save_context(inputs, {"answer": result["answer"]})
        return result


def azure_search_init(
    config: Configuration, embedding_model: OpenAIEmbeddings
) -> AzureSearch:
    """
    Load the vector store using the Azure Cognitive Search API.
    Args:
        config (Configuration): A configuration object containing API credentials and settings.

    Returns:
        AzureSearch: A vector store object.
    """
    # Extract Azure Cognitive Search credentials and settings from configuration

    vector_store_address = config.config["AZURE_VS"]["VS_ADDRESS"]
    vector_store_password = os.getenv("VECTOR_STORE_PSW")
    index_name = config.config["AZURE_VS"]["INDEX_NAME"]

    try:
        vector_store = AzureSearch(
            azure_search_endpoint=vector_store_address,
            azure_search_key=vector_store_password,
            index_name=index_name,
            embedding_function=embedding_model.embed_query,
            content_key="textContent",
            search_type="similarity",
        )
        return vector_store
    except requests.exceptions.RequestException as e:
        raise ConnectionError(
            f"Error interacting with Azure Cognitive Search: {str(e)}"
        )
    except Exception as e:
        raise e


def query_with_azure_search(azure_search: AzureSearch, query: str) -> Tuple:
    """
    Query the vector store using Azure Cognitive Search.
    Args:
        azure_search (AzureSearch): A vector store object.
        query (str): The query to search for.
    Returns:
        Tuple: A tuple containing the results and the query time.
    """
    # Query the vector store
    docs_to_return = azure_search.similarity_search(
        query=query, k=1, search_type="similarity"
    )
    return docs_to_return


def load_embedding(config: Configuration) -> OpenAIEmbeddings:
    """
    Load the embedding model using the OpenAI API.
    Parameters:
    - config (Configuration): A configuration object containing API credentials and settings.
    Returns:
    - OpenAIEmbeddings: An embedding object.
    """
    # Extract API credentials from the configuration
    api_key = config.api["api_key"]

    # Call the OpenAI API to generate embedding
    try:
        embedding_model = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            deployment="cv_embedding",
            openai_api_key=api_key,
            # openai_api_base=self.config["api_base"],
            # openai_api_type=self.config["api_type"],
        )
        return embedding_model
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Error interacting with OpenAI API: {str(e)}")
    except Exception as e:
        raise e


if __name__ == "__main__":
    # Initialize Configuration
    config = Configuration("config.json")

    # Initialize ChatOpenAIManagement
    chat = ChatOpenAIManagement(
        # config.api["deployment_name"],
        # config.api["api_base"],
        # config.api["api_version"],
        config.api["api_key"],
        # config.api["api_type"],
    )

    # System and Document Prompt
    system_template = """
        The user will ask you question about the resume of Charles, a Consultant Data Scientist at Capgemini Invent.
        Use the following pieces of context to answer the users question. 
        Only use the context that is relevant to the question.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Responds only to questions that are about Charles' resume.
        If the answer is using "you" or "your", replace it with "Charles" or "his".
        ----------------
        {context}"""

    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]

    chat_prompt = ChatPromptTemplate.from_messages(messages)

    template = """
        Content: {page_content}
    """
    document_prompt = PromptTemplate(
        input_variables=["page_content"], template=template
    )

    combine_docs_chain_kwargs = {
        "prompt": chat_prompt,
        "document_prompt": document_prompt,
    }

    # vector_store = VectorStoreManagement(
    #    load_embedding(config),
    #    config,
    # )

    azure_search = azure_search_init(config, load_embedding(config))
    # retriever = azure_search_retriever(azure_search)
    retriever = azure_search.as_retriever(
        search_type="similarity", search_kwargs={"k": 3}
    )
    # Create QA Chain
    # to_embed = "education"
    # embededded = load_embedding(config).embed_query(to_embed)
    # print(retriever.get_relevant_documents())
    qa = chat.create_qa(retriever, combine_docs_chain_kwargs)

    # Initialize memory and handler
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    handler = ThoughtsCallbackHandler()

    # Question
    question = "What is Charles' education?"

    # Execute
    result = chat.execute(question, memory, handler, qa)
    print(result)
