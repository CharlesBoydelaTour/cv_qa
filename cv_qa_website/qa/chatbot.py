from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

# pylint: disable=import-error
from .utils.bot_utils import (
    ChatOpenAIManagement,
    Configuration,
    azure_search_init,
    load_embedding,
)

from .utils.callbacks import ThoughtsCallbackHandler
from .utils.process_embedding import main_process


class ChatBotProcess:
    """A class used to manage the chatbot process"""

    def __init__(
        self,
        config: Configuration,
        chatmodel: ChatOpenAIManagement,
        system_template="""
        You are Charles' personal chatbot.
        The user will ask you question about the resume of Charles, a Data Scientist at Capgemini Invent.
        Use the following pieces of context to answer the users question. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Responds only to questions that are about Charles' resume.
        If the user is using "you" or "your", he wants to say "Charles" or "his" and not OpenAI or the chatbot.
        ----------------
        {context}""",
    ):
        # load configuaration file
        self.config = Configuration("config.json")

        # generate chat
        self.chat = chatmodel(
            #    config.api["deployment_name"],
            #    config.api["api_base"],
            # config.api["api_version"],
            config.api["api_key"],
            # config.api["api_type"],
        )

        self.system_template = system_template

        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        self.handler = ThoughtsCallbackHandler()
        self.vectorstore = azure_search_init(config, load_embedding(config))
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 3}
        )

    def generate_combine_docs(self) -> dict:
        """Generate the combine docs chain kwargs"""
        messages = [
            SystemMessagePromptTemplate.from_template(self.system_template),
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
        return combine_docs_chain_kwargs

    def create_qa_chain(self) -> ConversationalRetrievalChain:
        """Create the qa chain"""
        combine_docs_chain_kwargs = self.generate_combine_docs()
        qa = self.chat.create_qa(self.retriever, combine_docs_chain_kwargs)
        return qa

    def execute(self, question: str) -> str:
        """Execute the chatbot process"""
        qa = self.create_qa_chain()
        result = self.chat.execute(question, self.memory, self.handler, qa)
        return result

    def execute_answer(self, question: str) -> str:
        """Execute the chatbot process and return the answer"""
        result = self.execute(question)
        return result["answer"]


if __name__ == "__main__":
    # main_process(Configuration("config.json"))
    chatbot = ChatBotProcess(Configuration("config.json"), ChatOpenAIManagement)
    print(chatbot.execute_answer("Where did Charles studied?"))
