import autogen
from autogen import config_list_from_json

# Load the configuration
config_list = config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4"],  # Note: changed from "gpt4" to "gpt-4"
    },
)

# Ensure that the config_list is not empty
if not config_list:
    raise ValueError("No valid configurations found. Check your OAI_CONFIG_LIST file.")

# Set up the LLM configuration
llm_config = {
    "timeout": 600,
    "cache_seed": 42,
    "config_list": config_list,
    "temperature": 0,
}

# Create an AssistantAgent instance
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config=llm_config,
)

# Create a UserProxyAgent instance
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "web",
        "use_docker": True,
    },
    llm_config=llm_config,
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
Otherwise, TERMINATE with reason why the task is not solved.
If you plan to scrape any website Please provide the link of the website as well.
When providing information, please include sources or references when possible.""",
)

# Modify the initiate_chat call
response = user_proxy.initiate_chat(
    assistant,
    message="""Tell me about the IIT, Delhi.""",
)

# Save the assistant's response
assistant_response = response.get("content", "")  # Adjust based on the actual response structure

# Print or use the response as needed
print(assistant_response)
