import json
import re
from Compiler import throwAndExit

curr_word = 0
curr_line = 0
curr_token = 0


def nextWord(word):
    global curr_word
    global curr_line
    curr_word += 1
    if word == '\n':
        curr_word = 0
        curr_line += 1


def makeLexer(lexer):
    reglist = {}
    for lexems in lexer:
        keywords = lexems.get('keywords')
        if keywords is not None:
            temp = '^(' + '|'.join(keywords) + ')$'
            reglist.update({lexems['name']: re.compile(temp)})

        match = lexems.get('match')
        if match is not None:
            reglist.update({lexems['name']: re.compile(match)})
    return reglist


def tokenize(program, parser):
    lexer = makeLexer(parser['lexer'])
    words = lexer['special'].split(program)
    tokens = []

    for word in words:
        if (word is not None) and (word != ''):
            found = False
            for key in lexer:
                if lexer[key].match(word):
                    found = True
                    tokens.append({"keyword": word, "lexem": key, "word": curr_word, "line": curr_line})
                    nextWord(word)
                    break
            if not found:
                empty = {"keyword": None, "lexem": None, "word": curr_word, "line": curr_line}
                throwAndExit('unexpected symbol', 'Lexer', empty)
    tokens.append({"keyword": None, "lexem": 'eof', "word": curr_word, "line": curr_line})
    return tokens


def printAst(ast, offset=0):
    if ast is not None:
        if offset > 0:
            print(' ' * (offset - 1) * 2, '|')
        if ast['value'] is not None:
            print('{}{}({})'.format(' ' * offset * 2, ast['name'], ast['value']['keyword']))
        else:
            print('{}{}'.format(' ' * offset * 2, ast['name']))
        for node in ast['childs']:
            printAst(node, offset + 1)


def nextToken(tokens):
    global curr_token
    if curr_token < len(tokens) - 1:
        curr_token += 1


def checkLexem(lexem, tokens):
    global curr_token
    tok = tokens[curr_token]
    if tok['lexem'] == lexem:
        nextToken(tokens)
        return True
    return False


def checkKeyword(keyword, tokens):
    global curr_token
    tok = tokens[curr_token]
    if tok['keyword'] == keyword:
        nextToken(tokens)
        return True
    return False


def parseTerm(term, tokens, grammar):
    if term.get('lexem') is not None:
        if checkLexem(term['lexem'], tokens):
            if term['value']:
                return {'name': None, 'value': tokens[curr_token - 1], 'childs': []}
            return {'name': None, 'value': None, 'childs': []}

    if term.get('keyword') is not None:
        if checkKeyword(term['keyword'], tokens):
            if term['value']:
                return {'name': None, 'value': tokens[curr_token - 1], 'childs': []}
            return {'name': None, 'value': None, 'childs': []}

    if term.get('switch') is not None:
        for sw_term in term['switch']:
            temp = parseTerm(sw_term, tokens, grammar)
            if temp is not None:
                return temp

    if term.get('sequence') is not None:
        childs = []
        fault = None
        value = None
        crit = None
        pattern_fault = False
        term_found = False
        for seq_term in term['sequence']:
            temp = parseTerm(seq_term, tokens, grammar)
            if temp is None:
                if not seq_term['elect']:
                    if seq_term.get('crit') is not None:
                        crit = (seq_term['crit'], tokens[curr_token])
                        pattern_fault = True
                    else:
                        return fault
            else:
                term_found = True
                if temp['name'] is not None:
                    if seq_term['fault']:
                        fault = temp
                    if seq_term['child']:
                        childs.append(temp)
                if seq_term.get('value') and seq_term['value']:
                    value = temp['value']
        if pattern_fault:
            if term_found:
                if crit is not None:
                    throwAndExit(crit[0], 'Parser', crit[1])
            return fault
        return {'name': None, 'value': value, 'childs': childs}

    if term.get('split') is not None:
        list_term = term['split']['term']
        separator = term['split']['separator']
        childs = []
        value = None
        list_curr = parseTerm(list_term, tokens, grammar)
        sep_curr = parseTerm(separator, tokens, grammar)
        if sep_curr is None:
            return list_curr
        if list_curr is None:
            throwAndExit(term['list']['crit_left'], 'Parser', tokens[curr_token])
        value = sep_curr['value']
        childs.append(list_curr)
        while(sep_curr is not None):
            list_curr = parseTerm(list_term, tokens, grammar)
            sep_curr = parseTerm(separator, tokens, grammar)
            if list_curr is None:
                throwAndExit(term['list']['crit_right'], 'Parser', tokens[curr_token])
            childs.append(list_curr)
        return {'name': None, 'value': value, 'childs': childs}

    if term.get('list') is not None:
        list_term = term['list']['term']
        childs = []
        list_curr = parseTerm(list_term, tokens, grammar)
        if list_curr is None:
            return list_curr
        childs.append(list_curr)
        while list_curr is not None:
            childs.append(list_curr)
            list_curr = parseTerm(list_term, tokens, grammar)
        return {'name': None, 'value': None, 'childs': childs}

    if term.get('rule') is not None:
        return parseRule(term['rule'], tokens, grammar)
    return None


def parseRule(name, tokens, grammar):
    rule = grammar[name]
    node = parseTerm(rule['rule'], tokens, grammar)
    if node is None:
        return None
    if node['name'] is None:
        node['name'] = name
        return node
    return node


def parse(tokens, parser):
    grammar = parser['grammar']
    return parseRule(parser['main_rule'], tokens, grammar)
