"""
Tool definitions for HR Policy Assistant
Includes datetime and calculator tools
"""

from datetime import datetime
import re
from typing import Any


def datetime_tool() -> str:
    """
    Get current date and time.
    Returns current date in readable format.
    
    Returns:
        str: Formatted current date and time
    """
    try:
        current_time = datetime.now()
        return f"Current date and time: {current_time.strftime('%A, %B %d, %Y at %I:%M %p')}"
    except Exception as e:
        return f"Date information: {str(datetime.now())}"


def calculator_tool(expression: str) -> str:
    """
    Simple calculator tool that safely evaluates mathematical expressions.
    Supports basic arithmetic: +, -, *, /, %, **
    
    Args:
        expression: Mathematical expression as string
    
    Returns:
        str: Result of calculation or error message
    """
    try:
        # Remove whitespace
        expression = expression.strip()
        
        # Allow only safe characters
        safe_chars = set("0123456789+-*/%().e ")
        if not all(c in safe_chars for c in expression):
            return f"Invalid expression. Only numbers and basic operators (+, -, *, /, %, **) allowed."
        
        # Prevent dangerous operations
        if "import" in expression or "__" in expression:
            return "Invalid expression. Dangerous operations not allowed."
        
        # Evaluate safely using eval with restricted namespace
        result = eval(expression, {"__builtins__": {}}, {})
        
        # Return result
        return f"{expression} = {result}"
    
    except ZeroDivisionError:
        return "Error: Division by zero is not allowed."
    except SyntaxError:
        return f"Error: Invalid mathematical expression '{expression}'."
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


def get_tool_by_name(tool_name: str) -> callable:
    """
    Get tool function by name.
    
    Args:
        tool_name: Name of the tool
    
    Returns:
        callable: Tool function
    """
    tools = {
        "datetime": datetime_tool,
        "calculator": calculator_tool,
    }
    return tools.get(tool_name, None)


def execute_tool(tool_name: str, tool_input: str = None) -> str:
    """
    Execute a tool by name with optional input.
    
    Args:
        tool_name: Name of tool to execute
        tool_input: Input for the tool (optional)
    
    Returns:
        str: Tool result
    """
    try:
        if tool_name == "datetime":
            return datetime_tool()
        elif tool_name == "calculator":
            if tool_input is None:
                return "Calculator requires an expression."
            return calculator_tool(tool_input)
        else:
            return f"Unknown tool: {tool_name}"
    except Exception as e:
        return f"Tool execution error: {str(e)}"
