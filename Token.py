class Token:
    def __init__(self, kind, body, lineStart):
        self.kind = kind
        self.body = body
        self.lineStart = lineStart

    def print(self):
        return f"{self.kind}:{self.body}"

    def punct(self):
        return self.body if self.kind == 'PUNCT' else None

    def string(self):
        return self.body if self.kind == 'STRING' else None

    def num(self):
        return float(self.body) if self.kind == 'NUM' else None

    def ident(self):
        return self.body if self.kind == 'IDENT' and self.bool() == None else None

    def bool(self):
        return self.body == 'True' if self.kind == 'IDENT' and self.body in ['True', 'False'] else None

    def indent(self):
        return self.kind == 'INDENT'

    def dedent(self):
        return self.kind == 'DEDENT'
