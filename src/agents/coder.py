import operator
from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, BaseMessage, HumanMessage, ToolMessage

from src.core.config import settings
from src.agents.prompts import CODER_SYSTEM_PROMPT
from src.tools import TOOLS
from src.logger import log


class CoderState(TypedDict):
    task: str
    messages: Annotated[List[BaseMessage], operator.add]
    iterations: int
    is_complete: bool


class ToolExecutorNode:
    def __init__(self, tools):
        self.tool_map = {tool.name: tool for tool in tools}

    def __call__(self, state: CoderState):
        last_message = state["messages"][-1]
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return {"messages": []}

        tool_messages = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            log.info(f"Executing tool: {tool_name}")
            log.debug(f"Tool args: {tool_args}")

            try:
                tool = self.tool_map.get(tool_name)
                if not tool:
                    error_msg = f"Tool '{tool_name}' not found"
                    log.error(f"{error_msg}")
                    result = error_msg
                else:
                    result = tool.invoke(tool_args)
                    log.info(f" {tool_name} completed successfully")

            except Exception as e:
                error_msg = f"Error executing {tool_name}: {str(e)}"
                log.error(f"{error_msg}")
                result = error_msg

            tool_message = ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
                name=tool_name
            )
            tool_messages.append(tool_message)

        return {"messages": tool_messages}


class CoderAgent:
    def __init__(self, ):
        self.tools = TOOLS

        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.2,
        ).bind_tools(self.tools)

        self.graph = self._build_graph()

    def _agent_node(self, state: CoderState):
        messages = state["messages"]

        if len(messages) <= 1:
            messages = [
                SystemMessage(content=CODER_SYSTEM_PROMPT),
                HumanMessage(content=f"ACTUAL TASK: {state['task']}"),
            ]

        if len(messages) > 15:
            messages = [messages[0], messages[1]] + messages[-13:]

        response = self.llm.invoke(messages)

        return {"messages": [response], "iterations": state.get("iterations", 0) + 1}

    def _should_continue(self, state: CoderState):
        last_msg = state["messages"][-1]

        if last_msg.tool_calls:
            return "tools"

        if "DONE" in last_msg.content or state["iterations"] > 20:
            return END

        return "agent"

    def _build_graph(self):
        workflow = StateGraph(CoderState)

        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", ToolExecutorNode(self.tools))

        workflow.set_entry_point("agent")

        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "tools": "tools",
                "agent": "agent",
                END: END,
            }
        )

        workflow.add_edge("tools", "agent")
        return workflow.compile()

    def run(self, task_description: str, feedback: str = ""):
        input_msg = f"Task: {task_description}"
        if feedback:
            input_msg += f"\n\n!!! PREVIOUS ATTEMPT FAILED with feedback:\n{feedback}\nFix it."

        initial_state = {
            "task": input_msg,
            "messages": [SystemMessage(content=input_msg)],
            "iterations": 0,
            "is_complete": False,
        }

        final_state = self.graph.invoke(initial_state)
        return "Finished"
