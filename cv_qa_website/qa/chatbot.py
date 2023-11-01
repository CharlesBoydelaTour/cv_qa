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
        The user will ask you question about the resume of Charles. 
        Before we begin, here's some context about Charles' resume:
        - Charles is a Consultant Data Scientist at Capgemini Invent.
        - He has a MSc in Artificial Intelligence from CENTRALESUPELEC, a Master in Management from ESSEC Business School, and a Bachelor of Mechanical Engineering from the University of Leeds.
        - His professional experience includes roles as an AI Research Engineer Intern at THALES RESEARCH AND TECHNOLOGIES, a Consultant Data Scientist Intern at EKIMETRICS, and an intern at ALGECO SCOTSMAN.
        - He speaks French and English.
        - In addition to his academic and professional achievements, Charles has been involved in various associative commitments, including co-founding and presiding over PLONG’ESSEC, a student association dedicated to scuba diving and the preservation of marine biology.

        When users ask questions about Charles' resume, you should refer to the provided context to craft your responses. Follow these guidelines:
        1. Only use relevant information from the context to answer the user's question.
        2. Reformulate the context to create a concise and suitable response.
        3. Do not fabricate answers. If you don't have the information needed, simply state that you don't know.
        4. Limit your responses to questions about Charles' resume.
        5. Use third-person pronouns (e.g., "Charles" or "his") instead of second-person pronouns ("you" or "your") or first person pronouns ("I" or "my").
        Please keep in mind the above instructions while assisting users with their inquiries about Charles' resume.
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
            search_type="similarity", search_kwargs={"k": 2}
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
    print(chatbot.execute_answer("Why did Charles went to ESSEC?"))
