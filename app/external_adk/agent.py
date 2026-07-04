from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool

def process_expense(amount: int, description: str, justification: str = "") -> str:
    """Process an expense approval request.

    Args:
        amount: The expense amount in rupees.
        description: The description of what the expense was for.
        justification: The business justification. Required if amount >= 500.
    """
    if amount < 500:
        return f"Expense of ₹{amount} for '{description}' is auto-approved."
    elif amount <= 5000:
        if not justification or not justification.strip():
            return "Error: A business justification is required for expenses between ₹500 and ₹5000."
        return f"Expense of ₹{amount} for '{description}' is approved with justification: '{justification}'."
    else:
        return f"Expense of ₹{amount} for '{description}' is approved by manager."

def check_confirmation(amount: int, description: str, justification: str = "", **kwargs) -> bool:
    return amount > 5000

expense_tool = FunctionTool(
    process_expense,
    require_confirmation=check_confirmation
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="expense_approval_agent",
    description="An expense approval assistant with human-in-the-loop triage.",
    tools=[expense_tool],
    instruction="""
You are an Expense Approval Agent.

Your goal is to process expense approval requests using the `process_expense` tool.
For any expense request, determine the amount and description, and justification (if applicable).

Rules:
1. Under ₹500: Approve automatically by calling `process_expense` tool.
2. ₹500–₹5000: Ask the user for a business justification if they haven't provided one. Once you have the justification, call `process_expense` tool.
3. Above ₹5000: Call the `process_expense` tool. The system will automatically trigger a human manager approval step. Tell the user that the request has been submitted for manager approval.

Always call the `process_expense` tool to actually process the expense. Do NOT approve or reject expenses by yourself without calling the tool.
If the tool returns an error or is rejected, communicate that clearly to the user.
"""
)
