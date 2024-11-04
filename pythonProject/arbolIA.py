# behavior_tree.py
class Node:
    def __init__(self):
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def execute(self):
        raise NotImplementedError("This method should be overridden by subclasses")


class Selector(Node):
    def execute(self):
        for child in self.children:
            if child.execute():
                return True
        return False


class Sequence(Node):
    def execute(self):
        for child in self.children:
            if not child.execute():
                return False
        return True


class Condition(Node):
    def __init__(self, condition_func):
        super().__init__()
        self.condition_func = condition_func

    def execute(self):
        return self.condition_func()


class Action(Node):
    def __init__(self, action_func):
        super().__init__()
        self.action_func = action_func

    def execute(self):
        return self.action_func()