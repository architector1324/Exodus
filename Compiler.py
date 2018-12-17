import re


def throwAndExit(err, who, token):
    line = str(token['line'] + 1)
    word = str(token['word'] + 1)
    print('{}: {}({} line {} word)'.format(who, err, line, word))
    exit()


def translationFind(ast, regex_name, regex_value):
    match_name = re.match(regex_name, ast['name'])
    match_lexem = None
    match_keyword = None

    if ast['value'] is not None:
        match_lexem = re.match(regex_value['lexem'], ast['value']['lexem'])
        match_keyword = re.match(regex_value['keyword'], ast['value']['keyword'])

    if match_name and match_keyword and match_lexem:
        return ast

    for node in ast['childs']:
        test = translationFind(node, regex_name, regex_value)
        if test is not None:
            return test
    return None


def translationFindAll(ast, regex_name, regex_value):
    match_name = re.match(regex_name, ast['name'])
    match_lexem = None
    match_keyword = None

    result = []

    if ast['value'] is not None:
        match_lexem = re.match(regex_value['lexem'], ast['value']['lexem'])
        match_keyword = re.match(regex_value['keyword'], ast['value']['keyword'])

    if match_name and match_keyword and match_lexem:
        result.append(ast)

    for node in ast['childs']:
        test = translationFindAll(node, regex_name, regex_value)
        if len(test) > 0 and test != result:
            result.extend(test)
    return result


def compileTranslation(name, ast, translations):
    translation = translations[name]

    if translation.get('find') is not None:
        regex_name = translation['find']['name']
        regex_value = translation['find']['value']
        node = translationFind(ast, regex_name, regex_value)

        print(node)

    if translation.get('find_all') is not None:
        regex_name = translation['find_all']['name']
        regex_value = translation['find_all']['value']
        nodes = translationFindAll(ast, regex_name, regex_value)

        print(nodes)


def compile(ast, compiler):
    translator = compiler['translators'][compiler['main_translator']]
    main_translation = translator['main_translation']
    translations = translator['translations']

    compileTranslation(main_translation, ast, translations)
