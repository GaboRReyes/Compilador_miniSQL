"""
lexer.py — Analizador Léxico para MiniSQL en Español
"""

class Token:
    USAR            = 1001
    CREAR           = 1002
    ELIMINAR        = 1003
    MODIFICAR       = 1004
    SELECCIONAR     = 1005
    INSERTAR        = 1006
    ACTUALIZAR      = 1007
    BORRAR          = 1008
    MOSTRAR         = 1009
    CONCEDER        = 1010
    REVOCAR         = 1011
    TABLA           = 1012
    BASE_DE_DATOS   = 1013
    BASES           = 1014
    USUARIO         = 1015
    PERFIL          = 1016
    ESTRUCTURA      = 1017
    TODO            = 1018
    VALORES         = 1019
    EN              = 1020
    DESDE           = 1021
    DONDE           = 1022
    TENIENDO        = 1023
    LIMITE          = 1024
    ORDENAR         = 1025
    AGRUPAR         = 1026
    ASCENDENTE      = 1027
    DESCENDENTE     = 1028
    A               = 1029
    PARA            = 1030
    IDENTIFICADO_POR = 1031
    ENTEROS         = 1032
    CARACTERES      = 1033
    DECIMALES       = 1034
    NO_NULO         = 1035
    CONTRASEÑA      = 1036
    PERMISOS        = 1037
    TODOS_PRIVILEGIOS = 1038
    Y               = 1039
    O               = 1040

    OP_IGUAL        = 2001
    OP_DIFERENTE    = 2002
    OP_MENOR        = 2003
    OP_MAYOR        = 2004
    OP_MENOR_EQ     = 2005
    OP_MAYOR_EQ     = 2006
    OP_SUMA         = 2007
    OP_RESTA        = 2008
    OP_MULT         = 2009
    OP_DIV          = 2010

    PAREN_ABR       = 3001
    PAREN_CER       = 3002
    COMA            = 3003
    PUNTO_COMA      = 3004
    PUNTO           = 3005

    IDENTIFICADOR   = 6000
    ENTERO          = 7000
    FLOTANTE        = 8000
    CADENA_TEXTO    = 9000

    ERROR_LEXICO    = -1
    ERROR_NUM       = -2
    ERROR_CADENA    = -3
    ERROR_CHAR      = -10

    _NOMBRES = {
        1001:"USAR",1002:"CREAR",1003:"ELIMINAR",1004:"MODIFICAR",
        1005:"SELECCIONAR",1006:"INSERTAR",1007:"ACTUALIZAR",1008:"BORRAR",
        1009:"MOSTRAR",1010:"CONCEDER",1011:"REVOCAR",
        1012:"TABLA",1013:"BASE_DE_DATOS",1014:"BASES",
        1015:"USUARIO",1016:"PERFIL",1017:"ESTRUCTURA",
        1018:"TODO",1019:"VALORES",1020:"EN",1021:"DESDE",
        1022:"DONDE",1023:"TENIENDO",1024:"LIMITE",
        1025:"ORDENAR",1026:"AGRUPAR",1027:"ASCENDENTE",1028:"DESCENDENTE",
        1029:"A",1030:"PARA",1031:"IDENTIFICADO_POR",
        1032:"ENTEROS",1033:"CARACTERES",1034:"DECIMALES",1035:"NO_NULO",
        1036:"CONTRASEÑA",1037:"PERMISOS",1038:"TODOS_PRIVILEGIOS",
        1039:"Y",1040:"O",
        2001:"OP_IGUAL",2002:"OP_DIFERENTE",2003:"OP_MENOR",
        2004:"OP_MAYOR",2005:"OP_MENOR_EQ",2006:"OP_MAYOR_EQ",
        2007:"OP_SUMA",2008:"OP_RESTA",2009:"OP_MULT",2010:"OP_DIV",
        3001:"PAREN_ABR",3002:"PAREN_CER",3003:"COMA",
        3004:"PUNTO_COMA",3005:"PUNTO",
        6000:"IDENTIFICADOR",7000:"ENTERO",8000:"FLOTANTE",9000:"CADENA_TEXTO",
        -1:"ERROR_LEXICO",-2:"ERROR_NUM",-3:"ERROR_CADENA",-10:"ERROR_CHAR",
    }

    @classmethod
    def nombre(cls, codigo):
        for base in (6000,7000,8000,9000):
            if base <= codigo < base+1000:
                return cls._NOMBRES[base]
        return cls._NOMBRES.get(codigo, f"TOKEN_{codigo}")

    @classmethod
    def es_error(cls, codigo):
        return codigo < 0


PALABRAS_RESERVADAS = {
    "usar":Token.USAR,"crear":Token.CREAR,"eliminar":Token.ELIMINAR,
    "modificar":Token.MODIFICAR,"seleccionar":Token.SELECCIONAR,
    "insertar":Token.INSERTAR,"actualizar":Token.ACTUALIZAR,"borrar":Token.BORRAR,
    "mostrar":Token.MOSTRAR,"conceder":Token.CONCEDER,"revocar":Token.REVOCAR,
    "tabla":Token.TABLA,"base_de_datos":Token.BASE_DE_DATOS,"bases":Token.BASES,
    "usuario":Token.USUARIO,"perfil":Token.PERFIL,"estructura":Token.ESTRUCTURA,
    "todo":Token.TODO,"valores":Token.VALORES,"en":Token.EN,"desde":Token.DESDE,
    "donde":Token.DONDE,"teniendo":Token.TENIENDO,"limite":Token.LIMITE,
    "ordenar":Token.ORDENAR,"agrupar":Token.AGRUPAR,
    "ascendente":Token.ASCENDENTE,"descendente":Token.DESCENDENTE,
    "a":Token.A,"para":Token.PARA,"identificado_por":Token.IDENTIFICADO_POR,
    "enteros":Token.ENTEROS,"caracteres":Token.CARACTERES,
    "decimales":Token.DECIMALES,"no_nulo":Token.NO_NULO,
    "contraseña":Token.CONTRASEÑA,"permisos":Token.PERMISOS,
    "todos_privilegios":Token.TODOS_PRIVILEGIOS,
    "y":Token.Y,"o":Token.O,
}


class TokenResultado:
    def __init__(self, tipo, lexema, linea, columna):
        self.tipo    = tipo
        self.lexema  = lexema
        self.linea   = linea
        self.columna = columna

    def __repr__(self):
        nombre = Token.nombre(self.tipo)
        marca  = "X" if Token.es_error(self.tipo) else " "
        return (f"{marca} [{self.tipo:>5}] {nombre:<22} "
                f"'{self.lexema}'  L{self.linea}:C{self.columna}")


class AnalizadorLexico:
    def __init__(self, codigo):
        self.codigo  = codigo
        self.pos     = 0
        self.linea   = 1
        self.columna = 1
        self.tokens  = []
        self.errores = []
        self._tab_id  = {}; self._tab_ent = {}
        self._tab_flt = {}; self._tab_str = {}
        self._cnt_id  = 0;  self._cnt_ent = 0
        self._cnt_flt = 0;  self._cnt_str = 0

    def _peek(self, offset=0):
        idx = self.pos + offset
        return self.codigo[idx] if idx < len(self.codigo) else None

    def _avanzar(self):
        c = self.codigo[self.pos]; self.pos += 1
        if c == '\n': self.linea += 1; self.columna = 1
        else: self.columna += 1
        return c

    def _es_letra(self, c):
        return c.isalpha() or c in 'áéíóúüñÁÉÍÓÚÜÑ'

    def _reg_id(self, lex):
        k = lex.lower()
        if k not in self._tab_id:
            self._tab_id[k] = Token.IDENTIFICADOR + self._cnt_id; self._cnt_id += 1
        return self._tab_id[k]

    def _reg_ent(self, lex):
        if lex not in self._tab_ent:
            self._tab_ent[lex] = Token.ENTERO + self._cnt_ent; self._cnt_ent += 1
        return self._tab_ent[lex]

    def _reg_flt(self, lex):
        if lex not in self._tab_flt:
            self._tab_flt[lex] = Token.FLOTANTE + self._cnt_flt; self._cnt_flt += 1
        return self._tab_flt[lex]

    def _reg_str(self, lex):
        if lex not in self._tab_str:
            self._tab_str[lex] = Token.CADENA_TEXTO + self._cnt_str; self._cnt_str += 1
        return self._tab_str[lex]

    def _emit(self, tipo, lexema, lin, col):
        tok = TokenResultado(tipo, lexema, lin, col)
        self.tokens.append(tok)
        if Token.es_error(tipo):
            self.errores.append(f"L{lin}:C{col} [{Token.nombre(tipo)}] '{lexema}'")

    def analizar(self):
        while self.pos < len(self.codigo):
            self._siguiente_token()
        return self.tokens

    def _siguiente_token(self):
        while self.pos < len(self.codigo) and self._peek() in ' \t\r\n':
            self._avanzar()
        if self.pos >= len(self.codigo):
            return
        c = self._peek(); lin = self.linea; col = self.columna

        if c == '-' and self._peek(1) == '-':
            while self.pos < len(self.codigo) and self._peek() != '\n':
                self._avanzar()
            return

        if self._es_letra(c) or c == '_':
            self._leer_identificador(lin, col); return
        if c.isdigit():
            self._leer_numero(lin, col); return
        if c == "'":
            self._leer_cadena(lin, col); return

        self._avanzar()
        if   c == '=': self._emit(Token.OP_IGUAL, '=', lin, col)
        elif c == '<':
            if self._peek() == '>':   self._avanzar(); self._emit(Token.OP_DIFERENTE,'<>',lin,col)
            elif self._peek() == '=': self._avanzar(); self._emit(Token.OP_MENOR_EQ,'<=',lin,col)
            else: self._emit(Token.OP_MENOR,'<',lin,col)
        elif c == '>':
            if self._peek() == '=':   self._avanzar(); self._emit(Token.OP_MAYOR_EQ,'>=',lin,col)
            else: self._emit(Token.OP_MAYOR,'>',lin,col)
        elif c == '+': self._emit(Token.OP_SUMA,'+',lin,col)
        elif c == '-': self._emit(Token.OP_RESTA,'-',lin,col)
        elif c == '*': self._emit(Token.OP_MULT,'*',lin,col)
        elif c == '/': self._emit(Token.OP_DIV,'/',lin,col)
        elif c == '(': self._emit(Token.PAREN_ABR,'(',lin,col)
        elif c == ')': self._emit(Token.PAREN_CER,')',lin,col)
        elif c == ',': self._emit(Token.COMA,',',lin,col)
        elif c == ';': self._emit(Token.PUNTO_COMA,';',lin,col)
        elif c == '.': self._emit(Token.PUNTO,'.',lin,col)
        else:          self._emit(Token.ERROR_CHAR,c,lin,col)

    def _leer_identificador(self, lin, col):
        lexema = ''
        while self.pos < len(self.codigo):
            c = self._peek()
            if c and (self._es_letra(c) or c.isdigit() or c == '_'):
                lexema += self._avanzar()
            else:
                break
        lower = lexema.lower()
        if lower in PALABRAS_RESERVADAS:
            self._emit(PALABRAS_RESERVADAS[lower], lexema, lin, col)
        else:
            self._emit(self._reg_id(lexema), lexema, lin, col)

    def _leer_numero(self, lin, col):
        lexema = ''; es_float = False
        while self.pos < len(self.codigo) and self._peek().isdigit():
            lexema += self._avanzar()
        if self.pos < len(self.codigo) and self._peek() == '.':
            sig = self._peek(1)
            if sig and sig.isdigit():
                lexema += self._avanzar(); es_float = True
                while self.pos < len(self.codigo) and self._peek().isdigit():
                    lexema += self._avanzar()
                if self.pos < len(self.codigo) and self._peek() == '.':
                    lexema += self._avanzar()
                    while self.pos < len(self.codigo) and (self._peek().isdigit() or self._peek() == '.'):
                        lexema += self._avanzar()
                    self._emit(Token.ERROR_NUM, lexema, lin, col); return
        if self.pos < len(self.codigo) and self._es_letra(self._peek()):
            while self.pos < len(self.codigo) and (self._es_letra(self._peek()) or self._peek().isdigit() or self._peek()=='_'):
                lexema += self._avanzar()
            self._emit(Token.ERROR_NUM, lexema, lin, col); return
        if es_float: self._emit(self._reg_flt(lexema), lexema, lin, col)
        else:        self._emit(self._reg_ent(lexema), lexema, lin, col)

    def _leer_cadena(self, lin, col):
        lexema = self._avanzar(); cerrada = False
        while self.pos < len(self.codigo):
            c = self._avanzar(); lexema += c
            if c == "'": cerrada = True; break
            if c == '\n': break
        if cerrada: self._emit(self._reg_str(lexema), lexema, lin, col)
        else:       self._emit(Token.ERROR_CADENA, lexema, lin, col)

    def tabla_simbolos(self):
        lineas = ["\n------ TABLA DE SÍMBOLOS -----------------------------------"]
        secciones = [
            ("Palabras reservadas usadas", {t.lexema: t.tipo for t in self.tokens if 1000 < t.tipo < 2000}),
            ("Identificadores",   self._tab_id),
            ("Enteros",           self._tab_ent),
            ("Flotantes",         self._tab_flt),
            ("Cadenas de texto",  self._tab_str),
        ]
        for titulo, tabla in secciones:
            if tabla:
                lineas.append(f"|  {titulo}:")
                for lex, cod in tabla.items():
                    lineas.append(f"|    {cod:<7}  {Token.nombre(cod):<22}  {repr(lex)}")
        lineas.append("-----------------------------------------------------------")
        return '\n'.join(lineas)

    def resumen(self):
        total = len(self.tokens); err = len(self.errores)
        return f"  Total: {total}  |  Válidos: {total-err}  |  Errores: {err}"
