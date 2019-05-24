import logging
from scanner import get_next_token_s

logging.basicConfig(filename='parser.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.ERROR)
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Parser')

list_scan = [('KEYWORD', 'int', 1), ('ID', 'b', 1), ('SYMBOL', ';', 1), ('KEYWORD', 'int', 2), ('ID', 'foo', 2),('SYMBOL', '(', 2), ('KEYWORD', 'int', 2), ('ID', 'd', 2), ('SYMBOL', ',', 2), ('KEYWORD', 'int', 2), ('ID', 'e', 2), ('SYMBOL', ')', 2), ('SYMBOL', '{', 2), ('KEYWORD', 'int', 3), ('ID', 'f', 3), ('SYMBOL', ';', 3), ('KEYWORD', 'void', 4), ('ID', 'foo2', 4), ('SYMBOL', '(', 4), ('KEYWORD', 'int', 4), ('ID', 'k', 4), ('SYMBOL', '[', 4), ('SYMBOL', ']', 4), ('SYMBOL', ')', 4), ('SYMBOL', '{', 4), ('KEYWORD', 'return', 5), ('ID', 'k', 5), ('SYMBOL', '[', 5), ('NUM', 0, 5), ('SYMBOL', ']', 5), ('SYMBOL', '+', 5), ('ID', 'k', 5), ('SYMBOL', '[', 5), ('NUM', 1, 5), ('SYMBOL', ']', 5), ('SYMBOL', ';', 5), ('SYMBOL', '}', 6), ('KEYWORD', 'int', 7), ('ID', 'fff', 7), ('SYMBOL', '[', 7), ('NUM', 2, 7), ('SYMBOL', ']', 7), ('SYMBOL', ';', 7), ('ID', 'fff', 8), ('SYMBOL', '[', 8), ('NUM', 0, 8), ('SYMBOL', ']', 8), ('SYMBOL', '=', 8), ('ID', 'd', 8), ('SYMBOL', ';', 8), ('ID', 'fff', 9), ('SYMBOL', '[', 9), ('NUM', 1, 9), ('SYMBOL', ']', 9), ('SYMBOL', '=', 9), ('ID', 'd', 9), ('SYMBOL', '+', 9), ('NUM', 1, 9), ('SYMBOL', ';', 9), ('ID', 'f', 10), ('SYMBOL', '=', 10), ('ID', 'foo2', 10), ('SYMBOL', '(', 10), ('ID', 'fff', 10), ('SYMBOL', ')', 10), ('SYMBOL', ';', 10), ('ID', 'b', 11), ('SYMBOL', '=', 11), ('ID', 'e', 11), ('SYMBOL', '+', 11), ('ID', 'f', 11), ('SYMBOL', ';', 11), ('KEYWORD', 'while', 12), ('SYMBOL', '(', 12), ('ID', 'd', 12), ('NUM', 0, 12), ('SYMBOL', ')', 12), ('SYMBOL', '{', 12), ('ID', 'f', 13), ('SYMBOL', '=', 13), ('ID', 'f', 13), ('SYMBOL', '+', 13), ('ID', 'd', 13), ('SYMBOL', ';', 13), ('ID', 'd', 14), ('SYMBOL', '=', 14), ('ID', 'd', 14), ('SYMBOL', '-', 14), ('NUM', 1, 14), ('SYMBOL', ';', 14), ('KEYWORD', 'if', 15), ('SYMBOL', '(', 15), ('ID', 'd', 15), ('SYMBOL', '==', 15), ('NUM', 4, 15), ('SYMBOL', ')', 15), ('KEYWORD', 'break', 16), ('SYMBOL', ';', 16), ('KEYWORD', 'else', 17), ('SYMBOL', ';', 17), ('SYMBOL', '}', 18), ('KEYWORD', 'return', 20), ('ID', 'f', 20), ('SYMBOL', '+', 20), ('ID', 'b', 20), ('SYMBOL', ';', 20), ('SYMBOL', '}', 21), ('KEYWORD', 'int', 22), ('ID', 'arr', 22), ('SYMBOL', '[', 22), ('NUM', 3, 22), ('SYMBOL', ']', 22), ('SYMBOL', ';', 22), ('KEYWORD', 'void', 23), ('ID', 'main', 23), ('SYMBOL', '(', 23), ('KEYWORD', 'void', 23), ('SYMBOL', ')', 23), ('SYMBOL', '{', 23), ('KEYWORD', 'int', 24), ('ID', 'a', 24), ('SYMBOL', ';', 24), ('ID', 'a', 25), ('SYMBOL', '=', 25), ('SYMBOL', '-', 25), ('NUM', 3, 25), ('SYMBOL', '+', 25), ('SYMBOL', '+', 25), ('NUM', 11, 25), ('SYMBOL', ';', 25), ('ID', 'b', 26), ('SYMBOL', '=', 26), ('NUM', 5, 26), ('SYMBOL', '*', 26), ('ID', 'a', 26), ('SYMBOL', '+', 26), ('ID', 'foo', 26), ('SYMBOL', '(', 26), ('ID', 'a', 26), ('SYMBOL', ',', 26), ('ID', 'a', 26), ('SYMBOL', ')', 26), ('SYMBOL', ';', 26), ('ID', 'arr', 27), ('SYMBOL', '[', 27), ('NUM', 1, 27), ('SYMBOL', ']', 27), ('SYMBOL', '=', 27), ('ID', 'b', 27), ('SYMBOL', '+', 27), ('SYMBOL', '-', 27), ('NUM', 3, 27), ('SYMBOL', ';', 27), ('ID', 'arr', 28), ('SYMBOL', '[', 28), ('NUM', 2, 28), ('SYMBOL', ']', 28), ('SYMBOL', '=', 28), ('ID', 'foo', 28), ('SYMBOL', '(', 28), ('ID', 'arr', 28), ('SYMBOL', '[', 28), ('NUM', 0, 28), ('SYMBOL', ']', 28), ('SYMBOL', ',', 28), ('ID', 'arr', 28), ('SYMBOL', '[', 28), ('NUM', 1, 28), ('SYMBOL', ']', 28), ('SYMBOL', ')', 28), ('SYMBOL', ';', 28), ('KEYWORD', 'if', 29), ('SYMBOL', '(', 29), ('ID', 'b', 29), ('SYMBOL', '==', 29), ('NUM', 3, 29), ('SYMBOL', ')', 29), ('SYMBOL', '{', 29), ('ID', 'arr', 30), ('SYMBOL', '[', 30), ('NUM', 0, 30), ('SYMBOL', ']', 30), ('SYMBOL', '=', 30), ('SYMBOL', '-', 30), ('NUM', 7, 30), ('SYMBOL', ';', 30), ('SYMBOL', '}', 31), ('KEYWORD', 'else', 32), ('SYMBOL', '{', 33), ('KEYWORD', 'switch', 33), ('SYMBOL', '(', 33), ('ID', 'arr', 33), ('SYMBOL', '[', 33), ('NUM', 2, 33), ('SYMBOL', ']', 33), ('SYMBOL', ')', 33), ('SYMBOL', '{', 33), ('KEYWORD', 'case', 34), ('NUM', 2, 34), ('SYMBOL', ':', 34), ('ID', 'b', 35), ('SYMBOL', '=', 35), ('ID', 'b', 35), ('SYMBOL', '+', 35), ('NUM', 1, 35), ('SYMBOL', ';', 35), ('KEYWORD', 'case', 36), ('NUM', 3, 36), ('SYMBOL', ':', 36), ('ID', 'b', 37), ('SYMBOL', '=', 37), ('ID', 'b', 37), ('SYMBOL', '+', 37), ('NUM', 2, 37), ('SYMBOL', ';', 37), ('KEYWORD', 'return', 38), ('SYMBOL', ';', 38), ('KEYWORD', 'case', 39), ('NUM', 4, 39), ('SYMBOL', ':', 39), ('SYMBOL', '{', 40), ('ID', 'u', 40), ('SYMBOL', '=', 40), ('NUM', 5, 40), ('SYMBOL', ';', 40), ('ID', 'b', 41), ('SYMBOL', '=', 41), ('ID', 'u', 41), ('SYMBOL', '*', 41), ('SYMBOL', '-', 41), ('NUM', 123, 41), ('SYMBOL', ';', 41), ('KEYWORD', 'break', 42), ('SYMBOL', ';', 42), ('SYMBOL', '}', 42), ('KEYWORD', 'default', 43), ('SYMBOL', ':', 43), ('ID', 'b', 44), ('SYMBOL', '=', 44), ('ID', 'b', 44), ('SYMBOL', '-', 44), ('SYMBOL', '-', 44), ('NUM', 1, 44), ('SYMBOL', ';', 44), ('SYMBOL', '}', 45), ('SYMBOL', '}', 45), ('KEYWORD', 'return', 46), ('SYMBOL', ';', 46), ('SYMBOL', '}', 47), ('EOF', 'eof', 48)]


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
        ret['text'] = t[0].lower()
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
    def __init__(self, from_node, to_node, tpe, symbol=''):
        self.symbol = symbol
        self.from_node = from_node
        self.to_node = to_node
        self.type = tpe

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
            assert line[1] == '->', 'Line should start with Var and then ->. e.g: A -> blob blob'

            line = line[2:]

            if not line or line[-1] == '|':  # If a variable can be eps it should be it's last rule.
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


def recursive_parse(cur_component: Component, cur_token, depth: int, parse_tree):
    logging.info(f"Entering {cur_component} with {cur_token}")
    cur_state: State = cur_component.start_state

    parse_tree.append([depth, cur_component.symbol])
    depth += 1

    while not cur_state.accept:
        match = False

        for edge in cur_state.out_edges:
            if edge.type == 'T' and edge.symbol == cur_token['text']:
                parse_tree.append([depth, edge.symbol])
                cur_state = edge.to_node
                cur_token = get_next_token()
                match = True
                break
            if edge.type == 'V' and cur_token['text'] in dic_first[edge.symbol]:
                cur_token, parse_tree = recursive_parse(dic_components[edge.symbol], cur_token, depth, parse_tree)
                cur_state = edge.to_node
                match = True
                break

        if match:
            continue

        for edge in cur_state.out_edges:
            if edge.type == 'V' and dic_nullable[edge.symbol] and cur_token['text'] in dic_follow[edge.symbol]:
                cur_token, parse_tree = recursive_parse(dic_components[edge.symbol], cur_token, depth, parse_tree)
                cur_state = edge.to_node
                match = True
                break

        if match:
            continue

        for edge in cur_state.out_edges:
            if edge.type == 'E' and cur_token['text'] in dic_follow[cur_component.symbol]:
                parse_tree.append([depth, 'epsilon'])
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
    f = open('parse.txt', 'w+')
    for t in tree:
        f.write('|\t' * t[0] + t[1] + '\n')


def parse():
    current_component = dic_components[start_symbol]
    token = get_next_token()
    a, b = recursive_parse(current_component, token, 0, [])
    construct_parse_tree(b)


parse()
