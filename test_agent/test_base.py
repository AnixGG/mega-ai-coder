import pytest
from src.agents.coder import CoderAgent, CoderState, ToolExecutorNode
from langchain_core.messages import SystemMessage, HumanMessage


class MockTool:
    name = "mock_tool"

    def invoke(self, args):
        return f"processed {args}"


@pytest.fixture
def agent_with_mock_tool(monkeypatch):
    agent = CoderAgent()
    # Подмена инструментов
    agent.tools = [MockTool()]

    agent.graph = agent._build_graph()
    return agent


# Тест 1: Agent завершает выполнение

def test_agent_stops(agent_with_mock_tool):
    agent = agent_with_mock_tool
    final_state = agent.graph.invoke({
        "task": "Do nothing",
        "messages": [SystemMessage(content="Task: Do nothing")],
        "iterations": 0,
        "is_complete": False,
    })
    assert final_state["iterations"] <= 21


# Тест 2: ToolExecutor вызывается
def test_tool_executor_called():
    state = CoderState(
        task="Test tool",
        messages=[HumanMessage(content="Run tool")],
        iterations=0,
    )

    # Добавим tool_call вручную
    state["messages"][-1].tool_calls = [{"id": 1, "name": "mock_tool", "args": "arg1"}]

    tool_node = ToolExecutorNode([MockTool()])
    output = tool_node(state)
    assert len(output["messages"]) == 1
    assert "processed arg1" in output["messages"][0].content


# Тест 3: Message trimming работает
def test_message_trimming(agent_with_mock_tool):
    agent = agent_with_mock_tool
    state = {
        "task": "Long messages",
        "messages": [SystemMessage(content="sys")] + [HumanMessage(content=f"msg {i}") for i in range(20)],
        "iterations": 0,
        "is_complete": False,
    }
    result = agent._agent_node(state)

    messages = result["messages"]
    # Должны оставить максимум 15 сообщений: система и первый user + последние 13
    assert len(messages) <= 15