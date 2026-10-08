import time
import ast
import operator
from .base import BaseTool
from app.state import ToolResult

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Evaluates a basic mathematical expression safely."

    # Allowed operators
    _allowed_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg
    }

    def _eval(self, node):
        if isinstance(node, ast.Num): # <number>
            return node.n
        elif isinstance(node, ast.BinOp): # <left> <operator> <right>
            return self._allowed_ops[type(node.op)](self._eval(node.left), self._eval(node.right))
        elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
            return self._allowed_ops[type(node.op)](self._eval(node.operand))
        elif isinstance(node, ast.Constant): # for python 3.8+ compatibility
            return node.value
        else:
            raise TypeError(f"Unsupported operation or type: {type(node)}")

    def run(self, expression: str) -> ToolResult:
        start_time = time.time()
        try:
            if not expression or not expression.strip():
                return self._create_error_result("ValidationError", "Expression cannot be empty.", start_time)
            
            # parse to AST
            tree = ast.parse(expression, mode='eval')
            result = self._eval(tree.body)
            
            data = {
                "expression": expression,
                "result": result
            }
            return self._create_success_result(data, start_time)

        except SyntaxError:
            return self._create_error_result("SyntaxError", "Invalid mathematical expression.", start_time)
        except KeyError:
            return self._create_error_result("UnsupportedError", "Contains unsupported mathematical operators.", start_time)
        except Exception as e:
            return self._create_error_result("CalculationError", str(e), start_time)
