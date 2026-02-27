"""Basic arithmetic operations with history tracking."""


class Calculator:
    """Stateful calculator that records operation history."""

    def __init__(self):
        self.history: list[dict] = []

    def add(self, a: float, b: float) -> float:
        result = a + b
        self._record("add", a, b, result)
        return result

    def subtract(self, a: float, b: float) -> float:
        result = a - b
        self._record("subtract", a, b, result)
        return result

    def multiply(self, a: float, b: float) -> float:
        result = a * b
        self._record("multiply", a, b, result)
        return result

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self._record("divide", a, b, result)
        return result

    def power(self, base: float, exp: float) -> float:
        result = base**exp
        self._record("power", base, exp, result)
        return result

    def clear_history(self) -> None:
        self.history.clear()

    def last_result(self) -> float | None:
        if not self.history:
            return None
        return self.history[-1]["result"]

    def _record(self, op: str, a: float, b: float, result: float) -> None:
        self.history.append({"op": op, "a": a, "b": b, "result": result})
