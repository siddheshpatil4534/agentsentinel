from app.adapters.registry import AdapterRegistry
from app.adapters.agentsentinel_adapter import AgentSentinelAdapter
from app.adapters.adk_adapter import ADKAdapter
from app.adapters.langchain_adapter import LangChainAdapter
from app.adapters.crewai_adapter import CrewAIAdapter
from app.adapters.adk_adapter import ADKAdapter

registry = AdapterRegistry()

registry.register(
    AgentSentinelAdapter()
)

registry.register(
    ADKAdapter()
)

registry.register(
    LangChainAdapter()
)

registry.register(
    CrewAIAdapter()
)
registry.register(ADKAdapter())