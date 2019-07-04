import logging
from collections import defaultdict

logging.basicConfig(filename='generator.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
# logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('Generator')


class Lang:
    @staticmethod
    def assign(a, b):
        return f"(ASSIGN, {b}, {a}, )"

    @staticmethod
    def add(a, b, c):
        return f"(ADD, {b}, {c}, {a})"

    @staticmethod
    def mult(a, b, c):
        return f"(MULT, {b}, {c}, {a})"

    @staticmethod
    def sub(a, b, c):
        return f"(SUB, {b}, {c}, {a})"

    @staticmethod
    def jump(addr):
        return f"(JP, {addr}, , )"

    @staticmethod
    def print(addr):
        return f"(PRINT, {addr}, , )"


class Proc:
    BASE = 1000
    CODE_START = 0
    PTR_START = BASE
    DATA_START = 2 * BASE
    TEMP_START = 3 * BASE
    MAX_LINES = 4 * BASE

    SP = PTR_START + 0
    TP = PTR_START + 1
    AP = PTR_START + 2  # Activity Record Pointer
    TR = PTR_START + 3  # Temp Register
    AR = PTR_START + 4  # Temp A Register
    BR = PTR_START + 5  # Temp B Register

    """
    Activity Record
    It is:
        Control Link
        Action Link
        Temp Pointer
        Return Address
        Return Value
        <args>
        <local variables>
    """

    """
    Symbol Dictionary 
    key: 'varname'/'funcname'
    val: [ <occ1>, <occ2>, ... ]

    each occ is a dict with names
    - (type:'var', func_scope, scope, addr)
    - (type:'arr' , func_scope, scope, addr, size)
    - (type:'indarr', func_scope, scope, addr) Indirect Array (only function parameter)
    - (type:'func', func_scope, scope, addr, argc, ret)
    - (type:'special') -> for output function
    """
    sym_dict = defaultdict(list, {
        'output': [{'type': 'special', 'argc': 1, 'ret': 'void',
                    'scope': 0, 'func_scope': 0}]
    })

    decl_st = []
    sem_st = []

    scope_syms = defaultdict(list)
    scope_tmps = defaultdict(int)

    code = ['' for i in range(MAX_LINES)]
    curr_code_line = CODE_START
    curr_scope = 0
    curr_func_scope = 0
    curr_func_param = 0

    func_lv_off: list = [0]
    func_tmp_off: list = [0]
    func_jump_st: list = []

    @staticmethod
    def init():
        Proc._add_code([
            Lang.assign(Proc.TP, f"#{Proc.TEMP_START}"),
            Lang.assign(Proc.AP, f"#{Proc.DATA_START}"),
            Lang.add(Proc.TR, Proc.AP, '#2'),
            Lang.assign(f"@{Proc.TR}", Proc.TP),
            Lang.add(Proc.SP, Proc.AP, '#5'),
        ])

    @staticmethod
    def _validate_scope(name, token):
        if Proc.sym_dict['name']:
            if Proc.sym_dict['name'][-1]['type'] == 'special':
                logger.error(f"Line {token['line']}: Symbol {name} is special. Don't mess with it!")
                assert False
            else:
                if Proc.sym_dict['name'][-1]['scope'] <= Proc.curr_scope:
                    logger.error( f"Line {token['line']}: Function variable equal to function name")
                    assert False
                if Proc.sym_dict['name'][-1]['scope'] == Proc.curr_scope:
                    logger.error(f"Line {token['line']}: Symbol {name} is declared previously in current scope.")
                    assert False

    @staticmethod
    def _add(line, commands: list):
        Proc.code[line:line+len(commands)] = commands
        return len(commands)

    @staticmethod
    def _add_code(commands: list):
        Proc.curr_code_line += Proc._add(Proc.curr_code_line, commands) + 1

    @staticmethod
    def _push(var, val):
        return [
            Lang.assign(f"@{var}", val),
            Lang.add(var, var, '#1'),
        ]

    @staticmethod
    def _pop(var, num=1):
        return [
            Lang.sub(var, var, f'#{num}')
        ]

    @staticmethod
    def _push_sp(val):
        return Proc._push(Proc.SP, val)

    @staticmethod
    def _pop_sp(num=1):
        return Proc._pop(Proc.SP, num)

    @staticmethod
    def decl_var_inc_sp(token):
        Proc._add_code(Proc._push_sp('#0'))

    @staticmethod
    def decl_func_inc_sp(token):
        Proc._add_code(Proc._push_sp('#0'))

    @staticmethod
    def decl_arr_inc_sp(token):
        for i in range(Proc.decl_st[-1]):
            Proc._add_code(Proc._push_sp('#0'))

    @staticmethod
    def _push_tp(val):
        return Proc._push(Proc.TP, val)

    @staticmethod
    def _pop_tp(num=1):
        return Proc._pop(Proc.TP, num)

    @staticmethod
    def decl_pop(token):
        Proc.decl_st.pop()

    @staticmethod
    def decl_save_type(token):
        Proc.decl_st.append(token['text'])

    @staticmethod
    def decl_save_id(token):
        assert(token['text'] == 'id')
        Proc.decl_st.append(token['value'])

    @staticmethod
    def decl_save_num(token):
        assert(token['text'] == 'num')
        Proc.decl_st.append(token['value'])

    @staticmethod
    def decl_save_var(token):
        assert len(Proc.decl_st) >= 2
        Proc._validate_scope(Proc.decl_st[-1], token)

        name = Proc.decl_st.pop()
        tpe = Proc.decl_st.pop()

        if tpe == 'void':
            logger.error(f"Line {token['line']: Undefined variable type. Will use int instead.}")

        Proc.sym_dict[name].append({
            'type': 'var',
            'func_scope': Proc.curr_func_scope,
            'scope': Proc.curr_scope,
            'addr': Proc.func_lv_off[-1]
        })

        Proc.scope_syms[Proc.curr_scope].append(name)

        Proc.func_lv_off[-1] += 1

    @staticmethod
    def decl_save_arr(token):
        assert len(Proc.decl_st) >= 3
        Proc._validate_scope(Proc.decl_st[-2], token)

        sz = Proc.decl_st.pop()
        name = Proc.decl_st.pop()
        tpe = Proc.decl_st.pop()

        if tpe == 'void':
            logger.error(f"Line {token['line']: Undefined array type. Will use int instead.}")

        Proc.sym_dict[name].append({
            'type': 'arr',
            'func_scope': Proc.curr_func_scope,
            'scope': Proc.curr_scope,
            'addr': Proc.func_lv_off[-1],
            'size': sz
        })

        Proc.scope_syms[Proc.curr_scope].append(name)

        Proc.func_lv_off[-1] += sz

    @staticmethod
    def decl_save_func_arr(token):
        assert len(Proc.decl_st) >= 2
        Proc._validate_scope(Proc.decl_st[-1], token)

        name = Proc.decl_st.pop()
        tpe = Proc.decl_st.pop()

        if tpe == 'void':
            logger.error(f"Line {token['line']: Undefined ref array type. Will use int instead.}")

        Proc.sym_dict[name].append({
            'type': 'indarr',
            'func_scope': Proc.curr_func_scope,
            'scope': Proc.curr_scope,
            'addr': Proc.func_lv_off[-1]
        })

        Proc.scope_syms[Proc.curr_scope].append(name)

        Proc.func_lv_off[-1] += 1

    @staticmethod
    def decl_save_func(token):
        assert len(Proc.decl_st) >= 2
        Proc.curr_scope -= 1  # Actually function belongs to previous scope

        Proc._validate_scope(Proc.decl_st[-1], token)

        name = Proc.decl_st.pop()
        tpe = Proc.decl_st.pop()
        param = Proc.curr_func_param

        Proc.func_jump_st.append(Proc.curr_code_line)
        Proc.curr_code_line += 1

        Proc.sym_dict[name].append({
            'type': 'func',
            'func_scope': Proc.curr_func_scope-1,
            'scope': Proc.curr_scope,
            'addr': Proc.curr_code_line,
            'ret': tpe,
            'argc': param
        })

        Proc.scope_syms[Proc.curr_scope].append(name)

        Proc.func_lv_off[-2] += 1

        Proc.curr_scope += 1

    @staticmethod
    def func_reset_param(token):
        Proc.curr_func_param = 0

    @staticmethod
    def func_inc_param(token):
        Proc.curr_func_param += 1

    @staticmethod
    def scope_func_begin(token):
        Proc.curr_func_scope += 1
        Proc.func_lv_off.append(5)
        Proc.func_tmp_off.append(0)

    @staticmethod
    def scope_begin(token):
        Proc.curr_scope += 1

    @staticmethod
    def scope_end(token):
        Proc._add_code(Proc._pop_sp(len(Proc.scope_syms[Proc.curr_scope])))
        for name in Proc.scope_syms[Proc.curr_scope]:
            Proc.sym_dict[name].pop()

        Proc.func_lv_off[-1] -= len(Proc.scope_syms[Proc.curr_scope])
        Proc.scope_syms[Proc.curr_scope] = []

        Proc._add_code(Proc._pop_tp(Proc.scope_tmps[Proc.curr_scope]))
        Proc.func_tmp_off[-1] -= Proc.scope_tmps[Proc.curr_scope]
        Proc.scope_tmps[Proc.curr_scope] = 0

        Proc.curr_scope -= 1

    @staticmethod
    def scope_func_end(token):
        Proc.func_lv_off.pop()
        Proc.func_tmp_off.pop()
        Proc.curr_func_scope -= 1
        Proc._add(Proc.func_jump_st.pop(), [Lang.jump(Proc.curr_code_line)])

    @staticmethod
    def func_finalize(token):
        Proc._add_code([
            Lang.add(Proc.SP, Proc.AP, "#5"),
            Lang.sub(Proc.TP, Proc.TP, f"#{Proc.func_tmp_off[-1]}"),
            Lang.add(Proc.TR, Proc.AP, '#3'),
            Lang.jump(f"@{Proc.TR}")
        ])

    @staticmethod
    def pnum(token):
        assert token['text'] == 'num'
        Proc._add_code(Proc._push_tp(f"#{token['value']}"))
        Proc.sem_st.append(Proc.func_tmp_off[-1])
        Proc.func_tmp_off[-1] += 1
        Proc.scope_tmps[Proc.curr_scope] += 1
        print('$$$$$$$$$$$$$$$$$$$$$$$$$ ', Proc.func_tmp_off)

    @staticmethod
    def pname(token):
        assert token['text'] == 'id'
        Proc.sem_st.append(token['value'])

    @staticmethod
    def pvar(token):
        name = Proc.sem_st.pop()
        if not len(Proc.sym_dict[name]):
            logger.error(f"Line {token['line']}: Undeclared variable {name}")
            assert False

        entry = Proc.sym_dict[name][-1]

        if entry['type'] not in ['var', 'indarr', 'arr']:
            logger.error(f"Line {token['line']}: Undeclared variable {name}. {name} is a function")
            assert False

        if entry['type'] in ['indarr', 'var']:
            logger.warning(f"Line {token['line']}: Accessing array pointer")

        Proc._add_code([Lang.add(Proc.TR, Proc.AP, '#1')])  # To access link

        for i in range(Proc.curr_func_scope - entry['func_scope']):
            Proc._add_code([Lang.assign(Proc.TR, f"@{Proc.TR}")])

        Proc._add_code([Lang.add(Proc.TR, Proc.TR, f"#{entry['addr'] - 1}")])

        if entry['type'] == 'arr':  # Make arr indirect too
            Proc._add_code(Proc._push_tp(Proc.TR))
            Proc.func_tmp_off[-1] += 1
            Proc.scope_tmps[Proc.curr_scope] += 1

            Proc._add_code([Lang.sub(Proc.TR, f"@{Proc.TP}", '#1')])

        Proc.sem_st.append(Proc.func_tmp_off[-1])
        Proc.func_tmp_off[-1] += 1
        Proc.scope_tmps[Proc.curr_scope] += 1
        Proc._add_code(Proc._push_tp(Proc.TR))

    @staticmethod
    def pval(token):
        Proc._add_code([
            Lang.sub(Proc.TR, Proc.TP, '#1'),
            Lang.assign(Proc.BR, f'@{Proc.TR}'),
            Lang.assign(f'@{Proc.TR}', f'@{Proc.BR}')
        ])

    @staticmethod
    def parr(token):
        # TODO Write after testing var
        # TODO Include array bound checking
        pass

    @staticmethod
    def pfunc(token):
        name = Proc.sem_st[-1]
        if not len(Proc.sym_dict[name]):
            logger.error(f"Line {token['line']}: Undeclared function {name}")
            assert False

        entry = Proc.sym_dict[name][-1]

        if entry['type'] not in ['func', 'special']:
            logger.error(f"Line {token['line']}: Undeclared function {name}. {name} is a function")
            assert False

        Proc._add_code(Proc._push_sp(Proc.AP))
        Proc._add_code([Lang.add(Proc.TR, Proc.AP, '#1')] +
                       [Lang.assign(Proc.TR, f"@{Proc.TR}") for i in range(Proc.curr_func_scope -
                                                                           entry['func_scope'])] +
                        Proc._push_sp(Proc.TR) + Proc._push_sp('#0'))
        Proc._add_code(Proc._push_sp('#0') + Proc._push_sp('#0'))

        Proc.sem_st.append(0)
        print(Proc.sem_st)

    @staticmethod
    def _move_temp(rel, dest):
        Proc._add_code([
            Lang.add(dest, Proc.AP, '#2'),
            Lang.add(dest, f'@{dest}', f'#{rel}'),
            Lang.assign(dest, f'@{dest}')
        ])

    @staticmethod
    def func_add_arg(token):
        Proc._move_temp(Proc.sem_st.pop(), Proc.TR)
        Proc._add_code(Proc._push_sp(Proc.TR))
        Proc.sem_st[-1] += 1

    @staticmethod
    def func_call(token):
        argc = Proc.sem_st.pop()
        name = Proc.sem_st[-1]

        entry = Proc.sym_dict[name][-1]
        if argc != entry['argc']:
            logger.error(f"Line {token['line']}: {argc} arguments provided but {entry['argc']} required.")
            assert False

        if entry['type'] == 'func':
            Proc._add_code([
                Lang.sub(Proc.AP, Proc.SP, f'#{argc + 5}'),
                Lang.add(Proc.TR, Proc.AP, '#2'),
                Lang.assign(f'@{Proc.TR}', Proc.TP),
                Lang.add(Proc.TR, Proc.AP, '#3'),
                Lang.assign(f'@{Proc.TR}', f'#{Proc.curr_code_line + 6}'),
                Lang.jump(entry['addr'])
            ])
        elif name == 'output':
            Proc._add_code([
                Lang.sub(Proc.AP, Proc.SP, f'#{argc + 5}')])
            Proc._add_code([
                Lang.sub(Proc.SP, Proc.SP, '#1'),
                Lang.print(f'@{Proc.SP}')
            ])
        else:
            logger.error(f"Line {token['line']}: Unknown call type.")
            assert False

    @staticmethod
    def func_ret(token):
        name = Proc.sem_st.pop()
        entry = Proc.sym_dict[name][-1]

        if entry['ret'] == 'int':
            Proc._add_code(
                [Lang.add(Proc.TR, Proc.AP, '#4'),
                 Lang.assign(Proc.TR, f'@{Proc.TR}')] +
                Proc._push_tp(f'@{Proc.TR}')
            )
            Proc.sem_st.append(Proc.func_tmp_off[-1])
            Proc.func_tmp_off[-1] += 1
            Proc.scope_tmps[Proc.curr_scope] += 1
        else:
            Proc.sem_st.append(None)  # TODO Better error handling

        Proc._add_code([
            Lang.sub(Proc.SP, Proc.SP, '#5'),
            Lang.assign(Proc.AP, f"@{Proc.AP}"),
        ])

    @staticmethod
    def pop_sem_st(token):
        Proc.sem_st.pop()

    @staticmethod
    def handle_main(token):
        assert len(Proc.sym_dict['main']) == 1

        Proc.sem_st.append('main')

        Proc.pfunc(token)
        Proc.func_call(token)
        Proc.func_ret(token)

    @staticmethod
    def esym(token):
        Proc.sem_st.append(token['text'])

    @staticmethod
    def ecalc(token):
        Proc._move_temp(Proc.sem_st.pop(), Proc.AR)
        op = Proc.sem_st.pop()
        Proc._move_temp(Proc.sem_st.pop(), Proc.BR)

        calc_fun = Lang.add if op == '+' else Lang.sub if op == '-' else Lang.mul
        Proc._add_code([calc_fun(Proc.TR, Proc.TR, Proc.TR)] + Proc._push_tp(Proc.TR))

        Proc.sem_st.append(Proc.func_lv_off)

        Proc.func_lv_off[-1] += 1
        Proc.scope_tmps[Proc.curr_scope] += 1


def process_actions(action_list : list, curr_token):
    logger.info( f"{action_list} {curr_token}")
    for action in action_list:
        try:  # TODO: This exception should never occur
            getattr(Proc, action)(curr_token)
        except AttributeError as e:
            print(e)

    print('~~~~~~~~~~~~')
    print(action_list)
    print(curr_token)
    print(Proc.sem_st)
    print(Proc.sym_dict)
    print(Proc.curr_scope, Proc.curr_func_scope)
    print(Proc.scope_syms, Proc.scope_tmps)
    return


def print_code():
    with open("code.out", 'w') as f:
        lines = ('\n'.join(Proc.code).strip()).split('\n')
        lines = map(lambda tup: f'{tup[0]}\t{tup[1]}', enumerate(lines))
        f.write('\n'.join(lines))


Proc.init()
