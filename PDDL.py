from enum import Enum
from sys import argv, stdin
from typing import Self, Optional, Callable
from datetime import datetime


class TokenType(Enum):
    COMMENT = "Comment"
    PREDIACTE = "Predicate"
    CONSTANT = "Constant"
    ACTION = "Action"
    PRECONDITION = "Precondition"
    PRENEGCONDITION = "Negative-PreCondition"
    DELACTION = "Delete-Action"
    ADDACTION = "Add-Action"
    VARIABLE = "Variable"


class Token:
    def __init__(self, ttype: TokenType, lexeme: str, parent: Self = None, children: list = None):
        self.token_type = ttype
        self.lexeme = lexeme
        self.parent = parent
        if children is None:
            self.children = []
        else:
            self.children = children

    def __str__(self) -> str:
        return f"{self.token_type}: {self.lexeme}"

    def __repr__(self) -> str:
        return self.__str__()

    def add_child(self, child: Self):
        self.children.append(child)
        child.parent = self


class Constant:
    def __init__(self, value: str, parent=None):
        self.value = value
        self.parent = parent

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Constant):
            return self.value == other.value
        else:
            return False

    def copy(self):
        return Constant(str(self.value), self.parent)


class Variable:
    def __init__(self, value: str, parent=None):
        self.value = value
        self.parent = parent

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.value == other.value
        else:
            return False

    def copy(self):
        return Variable(str(self.value), self.parent)


class Predicate:
    def __init__(self, name: str, parent=None, became_true=-1):
        self.name = name
        self.terms = []
        self.parent = parent
        self.became_true = became_true

    def __str__(self):
        return f"{self.name}({', '.join([str(term) for term in self.terms])})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if self.name == other.name and len(self.terms) == len(other.terms):
            for i in range(len(self.terms)):
                if isinstance(self.terms[i], Constant) and isinstance(other.terms[i], Constant):
                    if self.terms[i].value != other.terms[i].value:
                        return False
            return True
        return False

    def copy(self):
        new = Predicate(self.name, self.parent)
        new.terms = [t.copy() for t in self.terms]
        return new


class Precondtions:
    def __init__(self, parent=None):
        self.predicates = []
        self.parent = parent

    def __str__(self):
        return f"pre: {' '.join([str(pred) for pred in self.predicates])}"

    def __repr__(self):
        return self.__str__()

    def copy(self):
        new = Precondtions(self.parent)
        new.predicates = [p.copy() for p in self.predicates]
        return new


class NegativePrecondtions:
    def __init__(self, parent=None):
        self.predicates = []
        self.parent = parent

    def __str__(self):
        return f"preneg: {' '.join([str(pred) for pred in self.predicates])}"

    def __repr__(self):
        return self.__str__()

    def copy(self):
        new = NegativePrecondtions(self.parent)
        new.predicates = [p.copy() for p in self.predicates]
        return new


class AddActions:
    def __init__(self, parent=None):
        self.predicates = []
        self.parent = parent

    def __str__(self):
        return f"add: {' '.join([str(pred) for pred in self.predicates])}"

    def __repr__(self):
        return self.__str__()

    def copy(self):
        new = AddActions(self.parent)
        new.predicates = [p.copy() for p in self.predicates]
        return new


class DeleteActions:
    def __init__(self, parent=None):
        self.predicates = []
        self.parent = parent

    def __str__(self):
        return f"del: {' '.join([str(pred) for pred in self.predicates])}"

    def __repr__(self):
        return self.__str__()

    def copy(self):
        new = DeleteActions(self.parent)
        new.predicates = [p.copy() for p in self.predicates]
        return new


class ActionCall:
    def __init__(self, name: str, terms: list[Constant], source_state=None):
        self.name = name
        self.terms = terms
        self.source_state = source_state

    def __str__(self):
        return f"{self.name} {' '.join([str(term) for term in self.terms])}"

    def __repr__(self):
        return self.__str__()


class State:
    def __init__(self, preds: list[Predicate], wrl, cost: int, source_action_call: Optional[ActionCall] = None):
        self.preds = preds
        self.world = wrl
        self.cost = cost
        self.source_action_call = source_action_call

    def __str__(self):
        return f"{self.cost} {self.source_action_call} -> {self.preds}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        for sp in self.preds:
            if sp not in other.preds:
                return False
        for op in other.preds:
            if op not in self.preds:
                return False
        return True

    def copy(self):
        return State(self.preds.copy(), self.world, self.cost, self.source_action_call)

    def print_acts(self):
        if self.source_action_call is None:
            return f""
        else:
            return f"{self.source_action_call.source_state.print_acts()}\n{self.cost - 1} {self.source_action_call}"


class Action:
    def __init__(self, name, wrl=None):
        self.name = name
        self.terms = []
        self.preconditions = None
        self.negative_preconditions = None
        self.add = None
        self.delete = None
        self.world = wrl

    def __str__(self):
        return f"{self.name} {' '.join([str(term) for term in self.terms])}\n" \
               f"{self.preconditions}\n" \
               f"{self.negative_preconditions}\n" \
               f"{self.add}\n{self.delete}"

    def __repr__(self):
        return self.__str__()

    def check_conditions(self, state: list[Predicate]) -> bool:
        for p in self.preconditions.predicates:
            if p not in state:
                return False
        for p in self.negative_preconditions.predicates:
            if p in state:
                return False
        return True

    def apply_actions(self, state: list[Predicate]) -> Optional[list[Predicate]]:
        if self.check_conditions(state):
            new_state = state.copy()
            for d in self.delete.predicates:
                new_state.remove(d)
            for a in self.add.predicates:
                new_state.append(a)
            return new_state
        return None

    def call(self, terms: list[Constant]) -> ActionCall:
        return ActionCall(self.name, terms)

    def ground(self, constants: list[Constant]) -> list[ActionCall]:
        calls = []
        params = self.expand_params(len(self.terms), constants)
        for p in params:
            calls.append(ActionCall(self.name, p))
        return calls

    @staticmethod
    def expand_params(terms: int, consts: list[Constant]) -> list[list[Constant]]:
        out = []
        if terms == 1:
            for i in consts:
                out.append([i])
        else:
            last = Action.expand_params(terms - 1, consts)
            for c in consts:
                l_copy = [ele.copy() for ele in last]
                for ele in l_copy:
                    ele.insert(0, c)
                out.extend(l_copy)
        return out

    def validate_call(self, call: ActionCall, state: list[Predicate]):
        if self.name != call.name:
            return False
        pre: Precondtions = self.preconditions.copy()
        npre: NegativePrecondtions = self.negative_preconditions.copy()
        for term_idx in range(len(self.terms)):
            for p in pre.predicates:
                for t_idx in range(len(p.terms)):
                    if p.terms[t_idx].value == self.terms[term_idx].value:
                        p.terms[t_idx] = call.terms[term_idx]
            for n in npre.predicates:
                for t_idx in range(len(n.terms)):
                    if n.terms[t_idx].value == self.terms[term_idx].value:
                        n.terms[t_idx] = call.terms[term_idx]

        for p in pre.predicates:
            if p not in state:
                return False
        for p in npre.predicates:
            if p in state:
                return False
        return True

    def apply_action(self, state: State, call: ActionCall, plus: bool = False):
        new_state = state.copy()
        subbed_add = self.add.copy()
        subbed_del = self.delete.copy()
        for t_idx in range(len(self.terms)):
            for a in subbed_add.predicates:
                for pt_idx in range(len(a.terms)):
                    if self.terms[t_idx] == a.terms[pt_idx]:
                        a.terms[pt_idx] = call.terms[t_idx]
            for d in subbed_del.predicates:
                for pt_idx in range(len(d.terms)):
                    if self.terms[t_idx] == d.terms[pt_idx]:
                        d.terms[pt_idx] = call.terms[t_idx]

        if not plus:
            for p in subbed_del.predicates:
                new_state.preds.remove(p)
        for a in subbed_add.predicates:
            new_state.preds.append(a.copy())
        new_state.cost += 1
        new_state.source_action_call = call
        return new_state


class World:
    def __init__(self,
                 predicates: list[Token],
                 constants: list[Token],
                 actions: list[Token],
                 inital_state: list[Token],
                 goal_state: list[Token]):
        self.predicates = [self.objectify(p) for p in predicates]
        self.constants = [self.objectify(c) for c in constants]
        self.actions = [self.objectify(a) for a in actions]
        self.inital_state = State([self.objectify(i_s) for i_s in inital_state], self, 0)
        self.goal_state = State([self.objectify(g_s) for g_s in goal_state], self, -1)

    @staticmethod
    def parse_predicate(token: Token):
        terms_list = token.lexeme.split("(")[1].split(", ")
        terms_list[-1] = terms_list[-1].rstrip(")")
        for term in terms_list:
            if term[0].isupper():
                token.add_child(Token(TokenType.CONSTANT, term))
            else:
                token.add_child(Token(TokenType.VARIABLE, term))

    @staticmethod
    def parse_predicates(preds: str) -> list[Token]:
        if preds == "":
            return []
        preds_list = [x + ")" for x in preds.split(") ")]
        preds_list[-1] = preds_list[-1][:-1]
        tokens = []
        for pred in preds_list:
            token = Token(TokenType.PREDIACTE, pred)
            World.parse_predicate(token)
            tokens.append(token)
        return tokens

    @staticmethod
    def parse_constants(consts: str) -> list[Token]:
        return [Token(TokenType.CONSTANT, c) for c in consts.split(" ")]

    @staticmethod
    def parse_action(action: list[str]) -> Token:
        tk_action = Token(TokenType.ACTION, "\n".join(action))

        terms = [Token(TokenType.VARIABLE, v, tk_action) for v in action[0].split(" ")[1:]]
        tk_action.children.append(terms)

        precond = Token(TokenType.PRECONDITION, action[1])
        [precond.add_child(x) for x in World.parse_predicates(action[1][5:])]
        prenegcond = Token(TokenType.PRENEGCONDITION, action[2])
        [prenegcond.add_child(x) for x in World.parse_predicates(action[2][8:])]
        addact = Token(TokenType.ADDACTION, action[4])
        [addact.add_child(x) for x in World.parse_predicates(action[4][5:])]
        delact = Token(TokenType.DELACTION, action[3])
        [delact.add_child(x) for x in World.parse_predicates(action[3][5:])]

        tk_action.add_child(precond)
        tk_action.add_child(prenegcond)
        tk_action.add_child(addact)
        tk_action.add_child(delact)

        return tk_action

    @staticmethod
    def parse(input_string: str):
        comments = []
        predicates = []
        constants = []
        initial = []
        goal = []
        actions = []
        lines = input_string.split("\n")
        skip = 0
        for line_idx in range(len(lines)):
            line = lines[line_idx]
            if line == "":
                continue
            if skip > 0:
                skip -= 1
                continue
            if line[0] == "#":
                token = Token(TokenType.COMMENT, line)
                comments.append(token)
                continue
            if line[0:12] == "predicates: ":
                predicates.extend(World.parse_predicates(line[12:]))
                continue
            if line[0:11] == "constants: ":
                constants.extend(World.parse_constants(line[11:]))
                continue
            if line[0:9] == "initial: ":
                initial.extend(World.parse_predicates(line[9:]))
                continue
            if line[0:6] == "goal: ":
                goal.extend(World.parse_predicates(line[6:]))
                continue
            if line[0].isupper():
                actions.append(World.parse_action(lines[line_idx:line_idx + 5]))
                skip = 4

        return comments, predicates, constants, actions, initial, goal

    def objectify(self, tk: Token, parent=None):
        if tk.token_type is TokenType.VARIABLE:
            return Variable(tk.lexeme, parent)
        elif tk.token_type is TokenType.CONSTANT:
            return Constant(tk.lexeme, parent)
        elif tk.token_type is TokenType.PREDIACTE:
            p = Predicate(tk.lexeme.split("(")[0], parent)
            terms = [self.objectify(term, p) for term in tk.children]
            p.terms = terms
            return p
        elif tk.token_type is TokenType.PRECONDITION:
            pc = Precondtions(parent)
            pc.predicates = [self.objectify(p, pc) for p in tk.children]
            return pc
        elif tk.token_type is TokenType.PRENEGCONDITION:
            npc = NegativePrecondtions(parent)
            npc.predicates = [self.objectify(p, npc) for p in tk.children]
            return npc
        elif tk.token_type is TokenType.ADDACTION:
            aa = AddActions(parent)
            aa.predicates = [self.objectify(p, aa) for p in tk.children]
            return aa
        elif tk.token_type is TokenType.DELACTION:
            da = DeleteActions(parent)
            da.predicates = [self.objectify(p, da) for p in tk.children]
            return da
        elif tk.token_type is TokenType.ACTION:
            a = Action(tk.lexeme.split(" ")[0], self)
            a.terms = [self.objectify(term, a) for term in tk.children[0]]
            a.preconditions = self.objectify(tk.children[1], a)
            a.negative_preconditions = self.objectify(tk.children[2], a)
            a.add = self.objectify(tk.children[3], a)
            a.delete = self.objectify(tk.children[4], a)
            return a

    def get_action_by_name(self, action_name: str) -> Optional[Action]:
        for a in self.actions:
            if a.name == action_name:
                return a
        return

    def ground(self, cur_state: State, print_calls=False) -> list[ActionCall]:
        calls = []
        valid_calls = []
        for a in self.actions:
            calls.extend(a.ground(self.constants))
        for c in calls:
            if self.get_action_by_name(c.name).validate_call(c, cur_state.preds):
                valid_calls.append(c)
        for vc in valid_calls:
            vc.source_state = cur_state
        if print_calls:
            for c in valid_calls:
                print(c)
            if len(valid_calls) == 0:
                print("No actions")
        return valid_calls

    def wastar(self, heuristic: Callable, weight: float):
        open_nodes = [self.inital_state]
        closed = []
        generated = 0
        expanded = 0
        while True:
            if len(open_nodes) == 0 or open_nodes[0] is None:
                return
            state = open_nodes.pop(0)
            if len([x for x in state.preds if x in self.goal_state.preds]) == len(self.goal_state.preds):
                return state, generated, expanded
            else:
                valid_action_calls = self.ground(state)
                children = []
                for call in valid_action_calls:
                    children.append(self.get_action_by_name(call.name).apply_action(state, call))
                    generated += 1
                for child in children:
                    if child not in closed:
                        open_nodes.insert(0, child)
                closed.append(state)
                expanded += 1
            open_nodes.sort(key=lambda x: x.cost + weight * heuristic(self, x))


def h0(wrl, s):
    return 0


def hlits(wrl: World, s: State):
    p_false = len(wrl.goal_state.preds)
    for p in wrl.goal_state.preds:
        if p in s.preds:
            p_false -= 1
    return p_false


def hmax(wrl: World, s: State):
    t = 0
    Q = s.copy()
    while len(Q.preds) != 0 and len([x for x in Q.preds if x in wrl.goal_state.preds]) != len(wrl.goal_state.preds):
        Qp = Q.copy()
        Qp_children = []
        valid_action_calls = wrl.ground(Q)
        for call in valid_action_calls:
            Qp_children.append(wrl.get_action_by_name(call.name).apply_action(Q, call, plus=True))
        for child in Qp_children:
            for pred in child.preds:
                if pred not in Qp.preds:
                    Qp.preds.append(pred)
                    pred.became_true = t + 1
        Q = Qp.copy()
        t += 1
    return t


def hsum(wrl: World, s: State):
    t = 0
    Q = s.copy()
    while len(Q.preds) != 0 and len([x for x in Q.preds if x in wrl.goal_state.preds]) != len(wrl.goal_state.preds):
        Qp = Q.copy()
        Qp_children = []
        valid_action_calls = wrl.ground(Q)
        for call in valid_action_calls:
            Qp_children.append(wrl.get_action_by_name(call.name).apply_action(Q, call, plus=True))
        for child in Qp_children:
            for pred in child.preds:
                if pred not in Qp.preds:
                    Qp.preds.append(pred)
                    pred.became_true = t + 1
        Q = Qp.copy()
        t += 1
    return sum([x.became_true for x in Q.preds if x.became_true > 0])


if __name__ == "__main__":
    in_file = None
    w = 0
    h = "h0"
    try:
        w = float(argv[1])
        h = argv[2]
        in_file = argv[3]
    except IndexError:
        pass

    if in_file is None:
        in_str = stdin.read()
    else:
        with open(in_file, "r") as f:
            in_str = f.read()
    world_tokens = World.parse(in_str)
    world = World(world_tokens[1],
                  world_tokens[2],
                  world_tokens[3],
                  world_tokens[4],
                  world_tokens[5])

    if h == "h0":
        win_state = world.wastar(h0, w)
    elif h == "hlits":
        win_state = world.wastar(hlits, w)
    elif h == "hmax":
        win_state = world.wastar(hmax, w)
    elif h == "hsum":
        win_state = world.wastar(hsum, w)
    else:
        win_state = world.wastar(h0, w)

    if win_state is not None:
        print(f"{win_state[0].print_acts()}\n{win_state[1]} nodes generated\n{win_state[2]} nodes expanded")
    else:
        print("Solution could not be found.")
