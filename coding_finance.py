from autogen.coding import LocalCommandLineCodeExecutor
from autogen import ConversableAgent, AssistantAgent
import datetime
import os
from IPython.display import Image
import yfinance
import matplotlib.pyplot as plt



llm_config = {"model": "gpt-4-turbo", "api_key": "YOUR_API_KEY"}

executor = LocalCommandLineCodeExecutor(
    timeout=60,
    work_dir="code",
)

# code executor agent
code_executor_agent = ConversableAgent(
    name="code_executor_agent",
    llm_config=False,
    code_execution_config={"executor": executor},
    human_input_mode="ALWAYS",
    default_auto_reply=
    "Please continue. If everything is done, reply 'TERMINATE'.",
)

# code writer agent
code_writer_agent = AssistantAgent(
    name="code_writer_agent",
    llm_config=llm_config,
    code_execution_config=False,
    human_input_mode="NEVER",
)

code_writer_agent_system_message = code_writer_agent.system_message

# The task
today = datetime.datetime.now().date()
message = f"Today is {today}. "\
"Create a plot showing stock gain YTD for NVDA and TLSA. "\
"Make sure the code is in markdown code block and save the figure"\
" to a file ytd_stock_gains.png."""

chat_result = code_executor_agent.initiate_chat(
    code_writer_agent,
    message=message,
)



Image(os.path.join("code", "ytd_stock_gains.png"))

exit()

def get_stock_prices(stock_symbols, start_date, end_date):
    """Get the stock prices for the given stock symbols between
    the start and end dates.

    Args:
        stock_symbols (str or list): The stock symbols to get the
        prices for.
        start_date (str): The start date in the format 
        'YYYY-MM-DD'.
        end_date (str): The end date in the format 'YYYY-MM-DD'.
    
    Returns:
        pandas.DataFrame: The stock prices for the given stock
        symbols indexed by date, with one column per stock 
        symbol.
    """
    

    stock_data = yfinance.download(
        stock_symbols, start=start_date, end=end_date
    )
    return stock_data.get("Close")

def plot_stock_prices(stock_prices, filename):
    """Plot the stock prices for the given stock symbols.

    Args:
        stock_prices (pandas.DataFrame): The stock prices for the 
        given stock symbols.
    """
    

    plt.figure(figsize=(10, 5))
    for column in stock_prices.columns:
        plt.plot(
            stock_prices.index, stock_prices[column], label=column
                )
    plt.title("Stock Prices")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.savefig(filename)

# new executor with given functions
    executor = LocalCommandLineCodeExecutor(
    timeout=60,
    work_dir="coding",
    functions=[get_stock_prices, plot_stock_prices],
)
    code_writer_agent_system_message += executor.format_functions_for_prompt()
print(code_writer_agent_system_message)

# update agents with new system message
code_writer_agent = ConversableAgent(
    name="code_writer_agent",
    system_message=code_writer_agent_system_message,
    llm_config=llm_config,
    code_execution_config=False,
    human_input_mode="NEVER",
)

code_executor_agent = ConversableAgent(
    name="code_executor_agent",
    llm_config=False,
    code_execution_config={"executor": executor},
    human_input_mode="ALWAYS",
    default_auto_reply=
    "Please continue. If everything is done, reply 'TERMINATE'.",
)

chat_result = code_executor_agent.initiate_chat(
    code_writer_agent,
    message=f"Today is {today}."
    "Download the stock prices YTD for NVDA and TSLA and create"
    "a plot. Make sure the code is in markdown code block and "
    "save the figure to a file stock_prices_YTD_plot.png.",
)

Image(os.path.join("coding", "stock_prices_YTD_plot.png"))

def call_rag_chat():
    _reset_agents()

    # In this case, we will have multiple user proxy agents and we don't initiate the chat
    # with RAG user proxy agent.
    # In order to use RAG user proxy agent, we need to wrap RAG agents in a function and call
    # it from other agents.
    def retrieve_content(
        message: Annotated[
            str,
            "Refined message which keeps the original meaning and can be used to retrieve content for code generation and question answering.",
        ],
        n_results: Annotated[int, "number of results"] = 3,
    ) -> str:
        leader_assistant.n_results = n_results  # Set the number of results to be retrieved.
        _context = {"problem": message, "n_results": n_results}
        ret_msg = leader_assistant.message_generator(leader_assistant, None, _context)
        return ret_msg or message

    leader_assistant.human_input_mode = "NEVER"  # Disable human input for boss_aid since it only retrieves content.

    for caller in [engineer, planner, finance_bro, leader]:
        d_retrieve_content = caller.register_for_llm(
            description="retrieve content for code generation and question answering.", api_style="function"
        )(retrieve_content)

    for exec in [engineer, executor]:
        exec.register_for_execution()(d_retrieve_content)

    groupchat = autogen.GroupChat(
        agents=[leader, leader_assistant, engineer, planner, executor, finance_bro],
        messages=[],
        max_round=20,
        allow_repeat_speaker=False,
    )

    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Start chatting with the boss as this is the user proxy agent.
    leader.initiate_chat(
        manager,
        message=task,
    )

    leader_assistant = RetrieveUserProxyAgent(
    name="Leader Assistant",
    is_termination_msg=termination_msg,
    human_input_mode="NEVER",
    default_auto_reply="Reply `TERMINATE` if the task is done.",
    max_consecutive_auto_reply=3,
    retrieve_config={
        "model": "gpt-4-turbo",
        "docs_path": "file:///Users/tursar.23/Desktop/Chart%201_62.avif",
        "collection_name": "groupchat-docs",
        "get_or_create": True,
    },
    code_execution_config=False,
    description="Assistant who has extra content retrieval power for solving difficult problems.",
)