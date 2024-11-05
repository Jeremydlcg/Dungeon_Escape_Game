# arbolIA.py

class Node:
    def run(self):
        raise NotImplementedError("This method should be overridden by subclasses")

class Selector(Node):
    def __init__(self, children=None):
        self.children = children or []

    def run(self):
        for child in self.children:
            result = child.run()
            if result != "failure":
                return result
        return "failure"

class Sequence(Node):
    def __init__(self, children=None):
        self.children = children or []

    def run(self):
        for child in self.children:
            result = child.run()
            if result != "success":
                return result
        return "success"

class Condition(Node):
    def __init__(self, condition):
        self.condition = condition

    def run(self):
        return "success" if self.condition() else "failure"

class Action(Node):
    def __init__(self, action):
        self.action = action

    def run(self):
        return self.action()