### 環境


Symbol = str


class Env(dict):
    def __init__(self, key_value_pair={}, outer=None):
        self.update(key_value_pair)
        self.outer = outer

    def find(self, key):
        if key in self:
            return self
        elif self.outer:
            return self.outer.find(key)
        else:
            raise Exception(f"{key} is not found. @Env.find()")


import math, operator as op

global_env = Env(
    key_value_pair={
        # システム関数
        "print": print,
        "exit": exit,
        # 数値,論理演算
        "+": op.add,
        "-": op.sub,
        "*": op.mul,
        "/": op.truediv,
        "!": op.not_,
        ">": op.gt,
        "<": op.lt,
        ">=": op.ge,
        "<=": op.le,
        "==": op.eq,
        # list操作
        "length": len,
        "cons": lambda x, y: [x] + y,
        "car": lambda x: x[0],
        "cdr": lambda x: x[1:],
        "append": op.add,
        "list": lambda *x: list(x),
        "list?": lambda x: isinstance(x, list),
        "null?": lambda x: x == [],
        # atom操作
        "symbol?": lambda x: isinstance(x, Symbol),
    }
)


### 評価(実行)
# 型判定ができていない e.g. defineのkey


def eval(exp, env=global_env):

    if isinstance(exp, Symbol):  # 変数解決
        return env.find(exp)[exp]

    elif not isinstance(exp, list):  # リテラル
        return exp

    elif len(exp) == 0:  # nullリスト
        return  # これでいい?

    else:
        # 組み込み構文
        if exp[0] == "quote":
            _, *cdr = exp
            return cdr

        elif exp[0] == "if":
            _, cond, true_exp, false_exp = exp
            if eval(cond, env):
                return eval(true_exp, env)
            else:
                return eval(false_exp, env)

        elif exp[0] == "while":
            _, cond, body = exp
            while eval(cond, env):
                eval(body, env)
            return

        elif exp[0] == "define":
            _, key, value = exp
            if not key in env:
                env[key] = eval(value)
            else:
                raise Exception(f"{key} is already defined. @eval()")
            return

        elif exp[0] == "set!":
            _, key, value = exp
            set_env = env.find(key)
            set_env[key] = eval(value, env)
            return

        elif exp[0] == "lambda":
            _, params, body = exp

            def arrow_func(*args):
                if len(args) != len(params):
                    raise Exception("Invalid number of arguments. @eval()")
                return eval(body, Env(zip(params, args), outer=env))

            return arrow_func

        elif exp[0] == "begin":
            _, *child_exps = exp
            for child_exp in child_exps:
                val = eval(child_exp, env)
            return val

        # elif exp[0] == "":
        #     return

        # カスタム関数
        else:
            exp_evaluated = [eval(elem, env) for elem in exp]
            proc = exp_evaluated.pop(0)
            return proc(*exp_evaluated)


### 構文解析以下


# atom
# リテラル, シンボルの分割
def atom(token):
    try:
        return int(token)
    except:
        try:
            return float(token)
        except:
            return str(token)


# parser
# 不十分
def parse(tokens):
    if len(tokens) == 0:
        return
        # raise SyntaxError("Invalid tokens. @parse()")
    token = tokens.pop(0)
    if token == "(":
        L = []
        while tokens[0] != ")":
            L.append(parse(tokens))
        tokens.pop(0)
        return L
    elif token == ")":
        raise SyntaxError("Unexpected ')'. @parse()")
    else:
        return atom(token)


# tokenizer
def tokenize(chars):
    return chars.replace("(", " ( ").replace(")", " ) ").split()


### 対話システム


# read-eval-print loop
def repl():
    tokens = []
    while True:
        val = input("lispyctomo> ")
        tokens.extend(tokenize(val))
        bracket_num = 0
        for index, token in enumerate(tokens):
            if token == "(":
                bracket_num += 1
            elif token == ")":
                bracket_num -= 1
            if bracket_num == 0:
                syntax_tree = parse(tokens[: index + 1])
                tokens = tokens[index + 1 :]
                # print(syntax_tree)
                eval(syntax_tree, global_env)
                break


if __name__ == "__main__":
    repl()
