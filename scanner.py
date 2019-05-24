import re

def giveRes(state1, state2, string):
    dic = {('number', 'start'): '(NUM, ' + string + ')',
           ('letter', 'start'): '(ID, ' + string + ')',
           ('number', 'error'): 'con',
           ('letter', 'error'): 'con',
           ('number', 'letter'): '(NUM, ' + string + ')',
           ('error', 'error'): ['(' + string + ', invalid input)', 'invalid input'],
           ('error', 'start'): ['(' + string + ', invalid input)', 'invalid input'],
           ('error', 'number'): ['(' + string + ', invalid input)', 'invalid input'],
           ('error', 'letter'): ['(' + string + ', invalid input)', 'invalid input'],
           ('letter', 'symbol'): '(ID, ' + string + ')',
           ('symbol', 'start'): '(SYMBOL, ' + string + ')',
           ('symbol', 'symbol'): '(SYMBOL, ' + string + ')',
           ('number', 'symbol'): '(NUM, ' + string + ')',
           ('error', 'symbol'): ['(' + string + ', invalid input)', 'invalid input'],
           ('symbol', 'error'): '(SYMBOL, ' + string + ')',
           ('symbol', 'number'): '(SYMBOL, ' + string + ')',
           ('symbol', 'letter'): '(SYMBOL, ' + string + ')',
           ('letter', 'equal'): '(ID, ' + string + ')',
           ('equal', 'start'): '(SYMBOL, ' + string + ')',
           ('number', 'equal'): '(NUM, ' + string + ')',
           ('equal', 'equal2'): 'con',
           ('equal2', 'equal'): '(SYMBOL, ' + string + ')',
           ('equal2', 'number'): '(SYMBOL, ' + string + ')',
           ('equal2', 'error'): '(SYMBOL, ' + string + ')',
           ('equal2', 'letter'): '(SYMBOL, ' + string + ')',
           ('equal2', 'symbol'): '(SYMBOL, ' + string + ')',
           ('error', 'equal'): ['(' + string + ', invalid input)', 'invalid input'],
           ('symbol', 'equal'): '(SYMBOL, ' + string + ')',
           ('equal', 'error'): '(SYMBOL, ' + string + ')',
           ('equal', 'number'): '(SYMBOL, ' + string + ')',
           ('equal', 'letter'): '(SYMBOL, ' + string + ')',
           ('equal', 'symbol'): '(SYMBOL, ' + string + ')',
           ('equal', 'start'): '(SYMBOL, ' + string + ')',
           ('equal2', 'start'): '(SYMBOL, ' + string + ')',
           ('number', 'comment'): '(NUM, ' + string + ')',
           ('letter', 'comment'): '(ID, ' + string + ')',
           ('symbol', 'comment'): '(SYMBOL, ' + string + ')',
           ('equal', 'comment'): '(SYMBOL, ' + string + ')',
           ('equal2', 'comment'): '(SYMBOL, ' + string + ')',
           ('error', 'comment'): ['(' + string + ', invalid input)', 'invalid input'],
           ('comment', 'number'): ['(' + string + ', invalid input)', 'invalid input'],
           ('comment', 'symbol'): ['(' + string + ', invalid input)', 'invalid input'],
           ('comment', 'letter'): ['(' + string + ', invalid input)', 'invalid input'],
           ('comment', 'error'): ['(' + string + ', invalid input)', 'invalid input'],
           ('comment', 'equal'): ['(' + string + ', invalid input)', 'invalid input'],
           ('comment', 'start'): ['(' + string + ', invalid input)', 'invalid input'],
           ('comment', 'total_comment'): 'break',
           ('comment', 'line_comment'): 'break',
           ('end_of_comment', 'start'): 'con'
           }
    if (state1 == state2 and not state2 == 'error' and not state2 == 'symbol' and not state2 == 'equal') or (state1 == 'start'):
        return 'cont', string
    elif dic[state1, state2] == 'con':
        return 'cont', string
    elif dic[state1, state2] == 'break':
        return 'break', string
    elif dic[state1, state2][1] == 'invalid input':
        return 'error', dic[state1, state2]
    else:
        return 'correct', dic[state1, state2]


def kind_t(str):
    if str.isdigit():
        return 'NUMBER'
    elif str == '*':
        return 'STAR'
    elif str in [',', ';', ':', '+', '-', ']', '[', '{', '}', '<', '(', ')']:
        return 'SYMBOL'
    elif str == '=':
        return 'EQUAL'
    elif str.isalpha():
        return 'LETTER'
    elif re.match('[ \t]+', str):
        return 'SKIP'
    elif str == '/':
        return 'COMMENT'
    elif re.match('\n', str):
        return 'NEWLINE'
    else:
        return 'ERROR'


def scan():
    list_result = []
    list_error = []
    g = open("result.txt", "w+")
    h = open("error_result.txt", "w+")
    state = 'start'
    keywords = {'if', 'else', 'void', 'int', 'while', 'break', 'continue', 'switch', 'default', 'case', 'return'}
    automata = {('start', 'NUMBER'): 'number',
                ('start', 'LETTER'): 'letter',
                ('number', 'NUMBER'): 'number',
                ('number', 'SKIP'): 'start',
                ('start', 'SKIP'): 'start',
                ('number', 'LETTER'): 'letter',
                ('letter', 'NUMBER'): 'letter',
                ('letter', 'SKIP'): 'start',
                ('letter', 'LETTER'): 'letter',
                ('letter', 'ERROR'): 'error',
                ('number', 'ERROR'): 'error',
                ('error', 'SKIP'): 'start',
                ('error', 'ERROR'): 'error',
                ('error', 'NUMBER'): 'number',
                ('error', 'LETTER'): 'letter',
                ('start', 'ERROR'): 'error',
                ('letter', 'SYMBOL'): 'symbol',
                ('symbol', 'SKIP'): 'start',
                ('symbol', 'SYMBOL'): 'symbol',
                ('symbol', 'ERROR'): 'error',
                ('symbol', 'NUMBER'): 'number',
                ('error', 'SYMBOL'): 'symbol',
                ('symbol', 'LETTER'): 'letter',
                ('start', 'SYMBOL'): 'symbol',
                ('number', 'SYMBOL'): 'symbol',
                ('number', 'EQUAL'): 'equal',
                ('letter', 'EQUAL'): 'equal',
                ('equal', 'EQUAL'): 'equal2',
                ('symbol', 'EQUAL'): 'equal',
                ('error', 'EQUAL'): 'equal',
                ('start', 'EQUAL'): 'equal',
                ('equal2', 'EQUAL'): 'equal',
                ('equal2', 'NUMBER'): 'number',
                ('equal2', 'LETTER'): 'letter',
                ('equal2', 'ERROR'): 'error',
                ('equal2', 'SYMBOL'): 'symbol',
                ('equal2', 'SKIP'): 'start',
                ('equal', 'NUMBER'): 'number',
                ('equal', 'LETTER'): 'letter',
                ('equal', 'ERROR'): 'error',
                ('equal', 'SYMBOL'): 'symbol',
                ('equal', 'SKIP'): 'start',
                ('number', 'COMMENT'): 'comment',
                ('letter', 'COMMENT'): 'comment',
                ('symbol', 'COMMENT'): 'comment',
                ('equal', 'COMMENT'): 'comment',
                ('equal2', 'COMMENT'): 'comment',
                ('start', 'COMMENT'): 'comment',
                ('error', 'COMMENT'): 'comment',
                ('comment', 'NUMBER'): 'number',
                ('comment', 'SYMBOL'): 'symbol',
                ('comment', 'LETTER'): 'letter',
                ('comment', 'ERROR'): 'error',
                ('comment', 'EQUAL'): 'equal',
                ('comment', 'SKIP'): 'start',
                ('comment', 'COMMENT'): 'line_comment',
                ('comment', 'STAR'): 'total_comment',
                ('total_comment', 'STAR'): 's',
                ('s', 'NUMBER'): 'total_comment',
                ('s', 'SYMBOL'): 'total_comment',
                ('s', 'LETTER'): 'total_comment',
                ('s', 'ERROR'): 'total_comment',
                ('s', 'EQUAL'): 'total_comment',
                ('s', 'SKIP'): 'total_comment',
                ('s', 'STAR'): 'total_comment',
                ('s', 'COMMENT'): 'end_of_comment',
                ('total_comment', 'NUMBER'): 'total_comment',
                ('total_comment', 'SYMBOL'): 'total_comment',
                ('total_comment', 'LETTER'): 'total_comment',
                ('total_comment', 'ERROR'): 'total_comment',
                ('total_comment', 'EQUAL'): 'total_comment',
                ('total_comment', 'SKIP'): 'total_comment',
                ('total_comment', 'COMMENT'): 'total_comment',
                ('letter', 'STAR'): 'symbol',
                ('symbol', 'STAR'): 'symbol',
                ('error', 'STAR'): 'symbol',
                ('start', 'STAR'): 'symbol',
                ('number', 'STAR'): 'symbol',
                ('equal2', 'STAR'): 'symbol',
                ('equal', 'STAR'): 'symbol',
                ('letter', 'NEWLINE'): 'start',
                ('number', 'NEWLINE'): 'start',
                ('error', 'NEWLINE'): 'start',
                ('equal', 'NEWLINE'): 'start',
                ('equal2', 'NEWLINE'): 'start',
                ('symbol', 'NEWLINE'): 'start',
                ('comment', 'NEWLINE'): 'start',
                ('start', 'NEWLINE'): 'start',
                ('line_comment', 'NEWLINE'): 'start',
                ('total_comment', 'NEWLINE'): 'total_comment',
                ('s', 'NEWLINE'): 'total_comment'
                }
    with open('code.txt') as f:
        result_number_of_line = 1
        error_number_of_line = 1
        for line in f:
            line = ''.join(line + ' ')
            myStr = []
            write_in_result = False
            write_in_error = False
            result_line_number_written = False
            error_line_number_written = False
            for i in range(len(line)):

                letter = line[i]
                current = letter
                kind = kind_t(letter)
                last_state = state
                state = automata[last_state, kind]
                if state == 'end_of_comment':
                    last_state = 'end_of_comment'
                    state = 'start'
                    myStr.clear()
                    current = ''
                if not state == 'total_comment' and not state == 's' and not state == 'end_of_comment':
                    a, b = giveRes(last_state, state, ''.join(myStr))
                    if a == 'break':
                        state = 'start'
                        break
                    if a == 'correct':
                        if not result_line_number_written:
                            g.write(str(result_number_of_line) + '. ')
                            result_line_number_written = True
                        if b[1:3] == 'ID' and b[5:-1] in keywords:
                            list_result.append(('KEYWORD', b[5: -1], result_number_of_line))
                            #print('(KEYWORD, ' + b[5:])
                            g.write('(KEYWORD, ' + b[5:])
                            yield ('KEYWORD', b[5: -1], result_number_of_line)
                        else:
                            x = ''
                            y = ''
                            if b[1: 3] == 'ID':
                                x = 'ID'
                                y = b.split()[1][: -1]
                            elif b[1: 4] == 'NUM':
                                x = 'NUM'
                                y = int(b.split()[1][: -1])
                            elif b[1: 7] == 'SYMBOL':
                                x = 'SYMBOL'
                                y = b.split()[1][: -1]
                            elif b[1: 8] == 'KEYWORD':
                                x = 'KEYWORD'
                                y = b.split()[1][: -1]
                            list_result.append((x, y, result_number_of_line))
                            #print(b)
                            g.write(b)
                            yield (x, y, result_number_of_line)
                        myStr.clear()
                        if not kind == 'SKIP':
                            myStr.append(current)
                        write_in_result = True
                    elif a == 'error':
                        if not error_line_number_written:
                            h.write(str(error_number_of_line) + '. ')
                            error_line_number_written = True
                        #list_result.append([b[0], error_number_of_line])
                        #print(b[0])
                        h.write(b[0])
                        #yield b[0]
                        myStr.clear()
                        if not kind == 'SKIP':
                            myStr.append(current)
                        write_in_error = True
                    else:
                        if not kind == 'SKIP':
                            myStr.append(current)
            result_number_of_line = result_number_of_line + 1
            error_number_of_line = error_number_of_line + 1
            if write_in_result:
                g.write('\n')
            if write_in_error:
                h.write('\n')
    yield ('EOF', 'eof', result_number_of_line)
    return list_result


list_scan = scan()


def get_next_token_s():
    try:
        return next(list_scan)
    except StopIteration:
        return None


