import autogen
import os
import boto3


config_list = [{
    "model": "anthropic.claude-3-sonnet-20240229-v1:0",  # Claude 3.5 Sonnet v2 model ID
    "api_type": "bedrock",
    "base_url": "bedrock-runtime",  # Bedrock runtime endpoint
    "credentials": {
        "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID"),
        "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        "aws_region": os.environ.get("AWS_REGION", "us-east-1")  # Default to us-east-1 if not specified
    }
}]

llm_config = {
    "timeout": 600,
    "cache_seed": 42,
    "config_list": config_list,
    "temperature": 0,
}

autogen_agent = autogen.AssistantAgent(
    name="assistant",
    llm_config=llm_config,
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "web",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    llm_config=llm_config,
    system_message="Reply TERMINATE if the task has been solved at full satisfaction. Otherwise, reply CONTINUE, or the reason why the task is not solved yet.",
)

from langgraph.graph import StateGraph, MessagesState


def call_autogen_agent(state: MessagesState):
    last_message = state["messages"][-1]
    response = user_proxy.initiate_chat(autogen_agent, message=last_message.content)
    # get the final response from the agent
    content = response.chat_history[-1]["content"]
    return {"messages": {"role": "assistant", "content": content}}


graph = StateGraph(MessagesState)
graph.add_node(call_autogen_agent)
graph.set_entry_point("call_autogen_agent")
graph = graph.compile()


