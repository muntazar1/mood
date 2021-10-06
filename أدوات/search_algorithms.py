import re

class CodeSearchAlgorithms:
    @staticmethod
    def object(string: str, object_type):
        codeobj = compile(string, "<decode>", "exec")
        store_length = {}

        def consts_walker(consts):
            for index, const in enumerate(consts):
                if type(const) == object_type:
                    store_length[len(const)] = const
                elif hasattr(const, "co_consts"):
                    consts_walker(const.co_consts)

        consts_walker(codeobj.co_consts)
        return store_length[sorted(store_length.keys())[-1]]

    @staticmethod
    def function(string: str, function_name):
        pattern: str = r"(" + function_name + r"(?:[\s]+)?\()"
        if len(func_poss := re.findall(pattern, string)) < 0:
            raise Exception()
        for func_pos in func_poss:
            function_body: str = string[string.find(func_pos):string.find(func_pos) + len(func_pos)]
            open_brackets: int = 1

            for _chr in string[string.find(func_pos) + len(func_pos):]:
                if _chr == "(":
                    open_brackets += 1
                elif _chr == ")":
                    open_brackets -= 1
                function_body += _chr
                if open_brackets == 0:
                    break
            string = string[string.find(function_body) + len(function_body):]
            yield function_body