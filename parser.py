#from scannerTwo import get_next_token

list_scan = [['(SYMBOL, ()', 1], ['(ID, id)', 1], ['(SYMBOL, ))', 1]]


def get_next_token():
    t = list_scan[0]
    list_scan.pop(0)
    return t


class State:
    def __init__(self):
        self.state_number = 0
        self.in_edges = {}
        self.out_edges = []
        self.isAccept = False


class Component:
    def __init__(self):
        self.symbol = ''
        self.start_state = None
        self.accept_state = None


class Edge:
    def __init__(self):
        self.symbol = ''
        self.fromNode = None
        self.toNode = None
        self.first = []
        self.follow = []
        self.isNullable = False
        self.type = ''


def buildDFA():
    dic_components = {}
    dic_first = {}
    dic_follow = {}
    dic_nullable = {}
    with open('first_follow.txt') as f:
        file_list = f.readlines()
        for i in range(0, len(file_list) - 4, 5):
            dic_first[file_list[i][: -1]] = file_list[i + 1][: -1].split()
            dic_follow[file_list[i][: -1]] = file_list[i + 2][: -1].split()
            if file_list[i + 3][: -1] == 'no':
                dic_nullable[file_list[i][: -1]] = False
            else:
                dic_nullable[file_list[i][: -1]] = True

    with open('myGrammar.txt') as f:
        start_symbol = f.readline().split()[0]

    with open('myGrammar.txt') as f:
        num_of_states = 0
        for line in f:
            line = line.strip()[:-1].split()
            start_state = State()
            start_state.state_number = num_of_states
            num_of_states += 1
            s = start_state
            accept_state = State()
            accept_state.isAccept = True
            accept_state.state_number = num_of_states
            num_of_states += 1
            for i in range(2, len(line)):
                if not line[i] == '|':
                    if i == len(line) - 1 and line[i] == ' ':      #epsilon
                        e = Edge()
                        e.symbol = line[i]
                        e.fromNode = start_state
                        e.toNode = accept_state
                        start_state.out_edges.append(e)
                    else:
                        if i < (len(line) - 1):
                            if line[i + 1] == '|':
                                ss = accept_state
                            else:
                                ss = State()
                                ss.state_number = num_of_states
                                num_of_states += 1
                        else:
                            ss = accept_state
                        e = Edge()
                        e.symbol = line[i]
                        e.fromNode = s
                        e.toNode = ss

                        if e.symbol[0].isupper():
                            e.type = 'V'
                            e.first = dic_first[line[i]]
                            e.follow = dic_follow[line[i]]
                            e.isNullable = dic_nullable[line[i]]
                        else:
                            e.type = 'T'

                        s.out_edges.append(e)

                        s = ss
                else:
                    s = start_state

            comp = Component()
            comp.start_state = start_state
            comp.accept_state = accept_state
            comp.symbol = line[0]
            dic_components[line[0]] = comp

    return dic_components, dic_first, dic_follow, dic_nullable, start_symbol


dic_components, dic_first, dic_follow, dic_nullable, start_symbol = buildDFA()


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
    current_state = current_component.start_state
    current_token = get_current_token(token)

    i = 0
    while i < len(current_state.out_edges):
        print('c_t:', current_token, 'within', current_component.symbol)
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

    if current_state.isAccept:
        return current_token


def parse():
    current_component = dic_components[start_symbol]
    token = get_next_token()
    recursive_parse(current_component, token)


parse()






