import json
import Parser

text = '123 + 34 + 45'

with open('Parsers/test.json') as f:
        parser = json.load(f)
        tokens = Parser.tokenize(text, parser)
        ast = Parser.parse(tokens, parser)
        Parser.printAst(ast)

        program_json = {"tokens": tokens, "ast": ast}
        with open('test.json', 'w') as of:
            json.dump(program_json, of, indent=4)

        # with open('Translators/test.json') as f2:
        #     compiler = json.load(f2)
        #     Compiler.compile(ast, compiler)
