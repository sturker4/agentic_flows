import autogen
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

llm_config = {"model": "gpt-4-turbo", "api_key": "sk-proj-O6wkpZmCHZqyLWeksHolT3BlbkFJZiZHfHzH5l3RIFqUaeSq"}


assistant = RetrieveAssistantAgent(
    name="assistant",
    system_message="You are a helpful assistant.",
    llm_config=llm_config,
)

ragproxyagent = RetrieveUserProxyAgent(
    name="College Application Blog Writer",
    code_execution_config=False,
    retrieve_config={
        "task": "qa",
        "get_or_create": True,
        "docs_path": [
        "https://www.bachelorsportal.com/countries/1/netherlands.html",
        'https://www.bachelorstudies.com/countries/netherlands'
        'https://www.timeshighereducation.com/student/advice/everything-you-need-know-about-studying-netherlands'
        'https://www.icesturkey.com/hollanda-universiteleri']   
    },
)

problem = """Write an article in a txt file to be published in the blog section of a university college admission 
counselling website. It should be intended for students who are interested in studying in Dutch 
universities as international students. Include ALL important details about all sorts of requirements, financial
aid and scholarship options, and every step included in applying and enrolling in the university, imiggration rules
carreer opportunities. Make it lengthy. Don't include information about daily life, or more general information not mentioned here. Make sure to 
optimize it for search engines. Also make sure that the information is strictly pertaining to undergraduate applicants.
"""

assistant.reset()
ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem=problem)