import logging
from scanner import get_next_token_s
from generator import process_actions

logging.basicConfig(filename='parser.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.ERROR)
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Parser')


def get_next_token():
    t = get_next_token_s()

    if not t:
        return None

    while t[0] in ['WHITESPACE', 'COMMENT']:
        t = get_next_token_s()

    ret = {'line': t[2]}

    if t[0] == 'KEYWORD' or t[0] == 'SYMBOL' or t[0] == 'EOF':
        ret['text'] = t[1]
    else:
        ret['text'] = t[0].lower()  # e.g: ID -> id
        ret['value'] = t[1]

    return ret


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
    def __init__(self, from_node, to_node, tpe, symbol, actions: list, post_actions: list = None):
        self.symbol = symbol
        self.from_node = from_node
        self.to_node = to_node
        self.type = tpe
        self.actions = actions
        self.post_actions = post_actions

        # logger.info("New edge created:", from_node, to_node, tpe, symbol)


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

    with open('grammar.txt') as f:
        start_sym = f.readline().split()[0]

    with open('grammar.txt') as f:
        for line in f:
            line = line.strip()[:-1].split()  # remove dot(.) in the end of line
            start_state = State()
            accept_state = State(accept=True)
            logging.info(line)

            var_sym = line[0]
            assert line[1] == '->', f'Line should start with Var and then ->. e.g: A -> blob blob + {line}'

            line = line[2:]

            def handle_eps(line):
                i = len(line) - 1
                actions = []
                while i >= 0 and line[i][0] == '#':
                    actions.append(line[i][1:])
                    i -= 1

                if i >= 0 and line[i] == '|':
                    edge = Edge(start_state, accept_state, 'E', '', actions)
                    start_state.out_edges.append(edge)
                    line = line[:i]
                return line

            line = handle_eps(line)

            line += ['|']

            cur_state: State = start_state
            cur_text: str = ''
            begin = True

            def t_type(text: str):
                if text[0] == '#':
                    return 'A'
                elif text[0].isupper():
                    return 'V'
                else:
                    return 'T'

            actions_queue = []
            final_actions = []

            for i, word in enumerate(line):
                if line[i] == '|':
                    assert cur_text, 'Rule should not be empty'
                    cur_state.out_edges.append(Edge(cur_state, accept_state, t_type(cur_text), cur_text, final_actions,
                                                    actions_queue))
                    actions_queue = []
                    final_actions = []
                    begin = True
                else:
                    if t_type(word) == 'A':
                        actions_queue.append(word[1:])
                    else:
                        if begin:
                            cur_state = start_state
                            cur_text = word
                            final_actions = actions_queue
                            actions_queue = []
                            begin = False
                        else:
                            state = State()
                            cur_state.out_edges.append(Edge(cur_state, state, t_type(cur_text),
                                                            cur_text, final_actions))
                            cur_state = state
                            cur_text = word
                            final_actions = actions_queue
                            actions_queue = []

            comp = Component()
            comp.start_state = start_state
            comp.accept_state = accept_state
            comp.symbol = var_sym
            components[var_sym] = comp

    return components, first, follow, nullable, start_sym


dic_components, dic_first, dic_follow, dic_nullable, start_symbol = build_diagram()


def recursive_parse(cur_component: Component, cur_token, depth: int, parse_tree):
    logging.info(f"Entering {cur_component} with {cur_token}")
    cur_state: State = cur_component.start_state

    parse_tree.append([depth, cur_component.symbol])
    depth += 1

    while not cur_state.accept:
        match = False

        for edge in cur_state.out_edges:
            if edge.type == 'T' and edge.symbol == cur_token['text']:
                process_actions(edge.actions, cur_token)
                parse_tree.append([depth, edge.symbol])
                cur_token = get_next_token()
                if edge.post_actions:
                    process_actions(edge.post_actions, cur_token)
                cur_state = edge.to_node
                match = True
                break
            if edge.type == 'V' and cur_token['text'] in dic_first[edge.symbol]:
                process_actions(edge.actions, cur_token)
                cur_token, parse_tree = recursive_parse(dic_components[edge.symbol], cur_token, depth, parse_tree)
                if edge.post_actions:
                    process_actions(edge.post_actions, cur_token)
                cur_state = edge.to_node
                match = True
                break

        if match:
            continue

        for edge in cur_state.out_edges:
            if edge.type == 'V' and dic_nullable[edge.symbol] and cur_token['text'] in dic_follow[edge.symbol]:
                process_actions(edge.actions, cur_token)
                cur_token, parse_tree = recursive_parse(dic_components[edge.symbol], cur_token, depth, parse_tree)
                if edge.post_actions:
                    process_actions(edge.post_actions, cur_token)
                cur_state = edge.to_node
                match = True
                break

        if match:
            continue

        for edge in cur_state.out_edges:
            if edge.type == 'E' and cur_token['text'] in dic_follow[cur_component.symbol]:
                parse_tree.append([depth, 'epsilon'])
                process_actions(edge.actions, cur_token)
                cur_state = edge.to_node  # It should go to final state
                assert cur_state == cur_component.accept_state, 'After going through eps should always reach accept'
                match = True
                break

        if match:
            continue

        assert cur_state != cur_component.start_state, "Parser should not stuck in start_state of of variable"
        assert len(cur_state.out_edges) == 1, "Any state other than start_state should have only one outgoing edge"

        edge = cur_state.out_edges[0]

        assert edge.type != 'E', 'Epsilon edge is only from start_state'

        if cur_token['text'] == 'eof':
            logger.error(f"#{cur_token['line']}: Syntax Error! Unexpected EOF.")
            break

        if edge.symbol == 'eof':
            logger.error(f"#{cur_token['line']}: Syntax Error! Malformed input.")
            break

        if edge.type == 'T':
            logger.error(f"#{cur_token['line']}: Syntax Error! Missing {edge.symbol}")
            cur_state = edge.to_node
        else:
            if cur_token['text'] not in dic_follow[edge.symbol]:
                logger.error(f"#{cur_token['line']}: Syntax Error! Unexpected {cur_token['text']}")
                cur_token = get_next_token()
            else:
                logger.error(f"#{cur_token['line']}: Syntax Error! Missing {edge.symbol} description")
                cur_state = edge.to_node

    logging.info(f"Returning {cur_component} with {cur_token}")

    return cur_token, parse_tree


def construct_parse_tree(tree):
    f = open('parse_table.txt', 'w+')
    for t in tree:
        f.write('|\t' * t[0] + t[1] + '\n')


def parse():
    current_component = dic_components[start_symbol]
    token = get_next_token()
    a, b = recursive_parse(current_component, token, 0, [])
    construct_parse_tree(b)


parse()
