#from scannerTwo import get_next_token

list_scan = [['(SYMBOL, ()', 1], ['(ID, id)', 1], ['(SYMBOL, ))', 1]]


def get_next_token():
    t = list_scan[0]
    list_scan.pop(0)
    return t


class State:
    instance_cnt = 0

    def __init__(self, accept: bool = False):
        self.state_number = State.instance_cnt
        State.instance_cnt += 1

        self.out_edges = []
        self.accept = accept

    def __str__(self):
        return f"({self.state_number}, {self.accept})"


class Component:
    def __init__(self):
        self.symbol = ''
        self.start_state = None
        self.accept_state = None

    def __str__(self):
        return self.symbol


class Edge:
    def __init__(self, from_node, to_node, tpe, symbol=''):
        self.symbol = symbol
        self.from_node = from_node
        self.to_node = to_node
        self.type = tpe

        # print("New edge created:", from_node, to_node, tpe, symbol)


def build_diagram():
    components = {}
    first = {}
    follow = {}
    nullable = {}
    with open('first_follow.txt') as f:
        file_list = list(map(lambda x: x.strip(), f.readlines()))
        for i in range(0, len(file_list), 5):
            first[file_list[i]] = file_list[i + 1].split()
            follow[file_list[i]] = file_list[i + 2].split()
            nullable[file_list[i]] = False if file_list[i + 3] == 'no' else True

    with open('myGrammar.txt') as f:
        start_sym = f.readline().split()[0]

    with open('myGrammar.txt') as f:
        for line in f:
            line = line.strip()[:-1].split()  # remove dot(.) in the end of line
            start_state = State()
            accept_state = State(accept=True)
            print(line)

            var_sym = line[0]
            assert line[1] == '->', 'Line should start with Var and then ->. e.g: A -> blob blob'

            line = line[2:]

            if not line or line[-1] == '|':  # If a variable can be eps it will be it's last rule.
                edge = Edge(start_state, accept_state, 'E', '')
                start_state.out_edges.append(edge)
                line = line[:-1]

            line += ['|']

            cur_state: State = start_state
            cur_text: str = ''
            begin = True

            def t_type(text: str):
                return 'V' if text[0].isupper() else 'T'

            for i, word in enumerate(line):
                if line[i] == '|':
                    assert cur_text, 'Rule should not be empty'
                    cur_state.out_edges.append(Edge(cur_state, accept_state, t_type(cur_text), cur_text))
                    begin = True
                else:
                    if begin:
                        cur_state = start_state
                        cur_text = word
                        begin = False
                    else:
                        state = State()
                        cur_state.out_edges.append(Edge(cur_state, state, t_type(cur_text), cur_text))
                        cur_state = state
                        cur_text = word

            comp = Component()
            comp.start_state = start_state
            comp.accept_state = accept_state
            comp.symbol = var_sym
            components[var_sym] = comp

    return components, first, follow, nullable, start_sym


dic_components, dic_first, dic_follow, dic_nullable, start_symbol = build_diagram()


def get_current_token(token):
    current_token = ''
    if token[0][1: 3] == 'ID':
        current_token = 'id'
    elif token[0][1: 4] == 'NUM':
        current_token = 'num'
    elif token[0][1: 7] == 'SYMBOL':
        current_token = token[0].split()[1][: -1]  # TODO: replace symbols in the grammar file
    elif token[0][1: 8] == 'KEYWORD':
        current_token = token[0].split()[1][: -1]
    return current_token


def recursive_parse(current_component: Component, token: str):
    print("Entering", current_component, "with", token)
    current_state: State = current_component.start_state
    current_token: str = get_current_token(token)

    while not current_state.accept:
        pass

    i = 0
    while i < len(current_state.out_edges):
        print('c_t:', current_token, 'within', current_component)
        edge = current_state.out_edges[i]
        if edge.type == 'T' and edge.symbol == current_token:
            current_state = edge.toNode
            token = get_next_token()
            current_token = get_current_token(token)
            i = 0
            continue
        elif edge.type == 'V':
            if current_token in dic_first[edge.symbol]:
                current_token = recursive_parse(dic_components[edge.symbol], token)
                current_state = edge.toNode
                i = 0
                continue
            elif edge.isNullable and (current_token in dic_follow[edge.symbol]):
                current_token = recursive_parse((dic_components[edge.symbol]), token)
                current_state = edge.toNode
                i = 0
                continue
        elif edge.symbol == ' ' and current_token in dic_follow[current_component.symbol]:
            current_state = current_component.accept_state
            i = 0
            continue
        i += 1

    if current_state.accept:
        print("Returning", current_component, "with", token)

        return current_token

    raise Exception("Should not reach here")


def parse():
    current_component = dic_components[start_symbol]
    token = get_next_token()
    recursive_parse(current_component, token)


parse()






