from lexer import Token
 
ERR_FIN_ENTRADA       = -11
ERR_TOKEN_INESPERADO  = -12
ERR_IDENTIFICADOR     = -13
ERR_SENTENCIA_INVALIDA = -14
ERR_VALOR_FALTANTE    = -15
ERR_OPERADOR_FALTANTE = -16
 
# ── Tipos de token lógico ────────────────────────────────────────────────────
_TIPO_Y = Token.Y   # 1039
_TIPO_O = Token.O   # 1040
 
# Operadores relacionales permitidos en condiciones
_OPS_RELACIONALES = {
    Token.OP_IGUAL, Token.OP_DIFERENTE,
    Token.OP_MENOR,  Token.OP_MAYOR,
    Token.OP_MENOR_EQ, Token.OP_MAYOR_EQ,
}
 
# ═══════════════════════════════════════════════════════════════════════
# NODO DEL ÁRBOL
# ═══════════════════════════════════════════════════════════════════════
class Nodo:
    def __init__(self, tipo, valor=None):
        self.tipo  = tipo
        self.valor = valor
        self.hijos = []
 
    def agregar(self, nodo):
        if nodo:
            self.hijos.append(nodo)
 
# ═══════════════════════════════════════════════════════════════════════
# ANALIZADOR SINTÁCTICO
# ═══════════════════════════════════════════════════════════════════════
class AnalizadorSintactico:
 
    def __init__(self, tokens):
        # Filtramos tokens de error léxico para no confundir al sintáctico
        self.tokens = [t for t in tokens if not Token.es_error(t.tipo)]
        self.i      = 0
        self.errores = []   # lista de tuplas (codigo, mensaje)
 
    # ── Navegación ────────────────────────────────────────────────────
    def actual(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else None
 
    def avanzar(self):
        self.i += 1
 
    def _tipo_actual(self):
        tok = self.actual()
        return tok.tipo if tok else None
 
    # Compara por lexema (case-insensitive)
    def match(self, palabra):
        tok = self.actual()
        if tok and tok.lexema.lower() == palabra.lower():
            self.avanzar()
            return True
        return False
 
    # Compara por código de token
    def match_tipo(self, tipo):
        tok = self.actual()
        if tok and tok.tipo == tipo:
            self.avanzar()
            return tok
        return None
 
    def esperar(self, palabra):
        tok = self.actual()
        if not tok:
            self.errores.append((ERR_FIN_ENTRADA,
                f"Se esperaba '{palabra}' pero llegó fin de entrada"))
            return False
        if tok.lexema.lower() != palabra.lower():
            self.errores.append((ERR_TOKEN_INESPERADO,
                f"Se esperaba '{palabra}' pero llegó '{tok.lexema}' "
                f"(L{tok.linea}:C{tok.columna})"))
            return False
        self.avanzar()
        return True
 
    def esperar_identificador(self):
        tok = self.actual()
        if not tok:
            self.errores.append((ERR_FIN_ENTRADA,
                "Se esperaba un IDENTIFICADOR pero llegó fin de entrada"))
            return None
        if Token.nombre(tok.tipo) == "IDENTIFICADOR":
            self.avanzar()
            return tok.lexema
        self.errores.append((ERR_IDENTIFICADOR,
            f"Se esperaba IDENTIFICADOR pero llegó '{tok.lexema}' "
            f"(L{tok.linea}:C{tok.columna})"))
        return None
 
    # Avanza hasta el próximo ';' para recuperarse de un error
    def _recuperar(self):
        while self.actual() and self.actual().lexema != ';':
            self.avanzar()
        if self.actual():
            self.avanzar()   # consume el ';'
 
    # ── Punto de entrada ──────────────────────────────────────────────
    def analizar(self):
        arbol = []
        while self.actual() is not None:
            nodo = self.sentencia()
            if nodo:
                arbol.append(nodo)
        return arbol
 
    def sentencia(self):
        tok = self.actual()
        if not tok:
            return None
        palabra = tok.lexema.lower()
        reglas = {
            "usar":         self.usar,
            "seleccionar":  self.seleccionar,
            "insertar":     self.insertar,
            "borrar":       self.borrar,
            "crear":        self.crear,
            "eliminar":     self.eliminar,
            "mostrar":      self.mostrar,
            "actualizar":   self.actualizar,
        }
        if palabra in reglas:
            return reglas[palabra]()
        self.errores.append((ERR_SENTENCIA_INVALIDA,
            f"Sentencia no válida: '{tok.lexema}' (L{tok.linea}:C{tok.columna})"))
        self.avanzar()
        self._recuperar()
        return None
 
    # ═══════════════════════════════════════════════════════════════════
    # CLÁUSULA WHERE — soporta N condiciones con Y / O
    # Gramática:
    #   condicion      → simple_cond { (Y | O) simple_cond }
    #   simple_cond    → IDENTIFICADOR operador valor
    #   operador       → = | <> | < | > | <= | >=
    #   valor          → IDENTIFICADOR | ENTERO | FLOTANTE | CADENA_TEXTO
    # ═══════════════════════════════════════════════════════════════════
    def condicion(self):
        """Parsea una o más condiciones unidas por Y / O."""
        nodo_where = Nodo("CONDICION")
 
        cond = self._condicion_simple()
        if not cond:
            return None
        nodo_where.agregar(cond)
 
        # Mientras haya Y (1039) u O (1040) seguimos consumiendo condiciones
        while True:
            tok = self.actual()
            if tok is None:
                break
            if tok.tipo == _TIPO_Y:
                self.avanzar()
                operador_logico = Nodo("OP_LOGICO", "Y")
                nodo_where.agregar(operador_logico)
                cond = self._condicion_simple()
                if not cond:
                    return None
                nodo_where.agregar(cond)
            elif tok.tipo == _TIPO_O:
                self.avanzar()
                operador_logico = Nodo("OP_LOGICO", "O")
                nodo_where.agregar(operador_logico)
                cond = self._condicion_simple()
                if not cond:
                    return None
                nodo_where.agregar(cond)
            else:
                break   # No es operador lógico: salimos del bucle
 
        return nodo_where
 
    def _condicion_simple(self):
        """Parsea: IDENTIFICADOR  operador  valor"""
        nodo = Nodo("COND_SIMPLE")
 
        col = self.esperar_identificador()
        if col is None:
            return None
        nodo.agregar(Nodo("COLUMNA", col))
 
        # Operador relacional
        tok = self.actual()
        if not tok:
            self.errores.append((ERR_OPERADOR_FALTANTE,
                "Se esperaba un operador relacional pero llegó fin de entrada"))
            return None
        if tok.tipo not in _OPS_RELACIONALES:
            self.errores.append((ERR_OPERADOR_FALTANTE,
                f"Se esperaba operador relacional pero llegó '{tok.lexema}' "
                f"(L{tok.linea}:C{tok.columna})"))
            return None
        nodo.agregar(Nodo("OPERADOR", tok.lexema))
        self.avanzar()
 
        # Valor: identificador, entero, flotante o cadena
        tok = self.actual()
        if not tok:
            self.errores.append((ERR_VALOR_FALTANTE,
                "Se esperaba un valor en la condición pero llegó fin de entrada"))
            return None
        nombre_tipo = Token.nombre(tok.tipo)
        if nombre_tipo not in ("IDENTIFICADOR", "ENTERO", "FLOTANTE", "CADENA_TEXTO"):
            self.errores.append((ERR_VALOR_FALTANTE,
                f"Se esperaba un valor en la condición pero llegó '{tok.lexema}' "
                f"(L{tok.linea}:C{tok.columna})"))
            return None
        nodo.agregar(Nodo("VALOR", tok.lexema))
        self.avanzar()
 
        return nodo
 
    # ═══════════════════════════════════════════════════════════════════
    # SELECCIONAR
    # Soporta: columnas separadas por coma, *, DONDE multi-cond,
    #          ORDENAR [ASCENDENTE|DESCENDENTE], LIMITE, AGRUPAR
    # ═══════════════════════════════════════════════════════════════════
    def seleccionar(self):
        nodo = Nodo("SELECT")
        if not self.esperar("seleccionar"):
            self._recuperar(); return None
 
        columnas = Nodo("COLUMNAS")
 
        # '*' o lista de identificadores separados por coma
        if self.match("todo") or self.match("*"):
            columnas.agregar(Nodo("COL", "*"))
        else:
            col = self.esperar_identificador()
            if col is None:
                self._recuperar(); return None
            columnas.agregar(Nodo("COL", col))
            while self.match(","):
                col = self.esperar_identificador()
                if col is None:
                    self._recuperar(); return None
                columnas.agregar(Nodo("COL", col))
 
        nodo.agregar(columnas)
 
        if not self.esperar("desde"):
            self._recuperar(); return None
 
        tabla = self.esperar_identificador()
        if tabla is None:
            self._recuperar(); return None
        nodo.agregar(Nodo("TABLA", tabla))
 
        # DONDE (opcional)
        if self.match("donde"):
            cond = self.condicion()
            if cond is None:
                self._recuperar(); return None
            nodo.agregar(cond)
 
        # AGRUPAR (opcional)
        if self.match("agrupar"):
            grupo = Nodo("GROUP_BY")
            col = self.esperar_identificador()
            if col:
                grupo.agregar(Nodo("COL", col))
            nodo.agregar(grupo)
 
        # ORDENAR (opcional)
        if self.match("ordenar"):
            orden = Nodo("ORDER_BY")
            if self.match("ascendente"):
                orden.agregar(Nodo("DIR", "ASC"))
            elif self.match("descendente"):
                orden.agregar(Nodo("DIR", "DESC"))
            else:
                orden.agregar(Nodo("DIR", "ASC"))  # default
            nodo.agregar(orden)
 
        # LIMITE (opcional)
        if self.match("limite"):
            tok = self.actual()
            if tok and Token.nombre(tok.tipo) == "ENTERO":
                nodo.agregar(Nodo("LIMITE", tok.lexema))
                self.avanzar()
 
        if not self.esperar(";"):
            self._recuperar(); return None
        return nodo
 
    # ═══════════════════════════════════════════════════════════════════
    # INSERTAR
    # ═══════════════════════════════════════════════════════════════════
    def insertar(self):
        nodo = Nodo("INSERT")
        if not self.esperar("insertar"):
            self._recuperar(); return None
        if not self.esperar("en"):
            self._recuperar(); return None
 
        tabla = self.esperar_identificador()
        if tabla is None:
            self._recuperar(); return None
        nodo.agregar(Nodo("TABLA", tabla))
 
        # Columnas opcionales entre paréntesis
        if self.match("("):
            cols = Nodo("COLUMNAS")
            while self.actual() and self.actual().lexema != ")":
                if self.actual().lexema == ",":
                    self.avanzar()
                    continue
                col = self.esperar_identificador()
                if col:
                    cols.agregar(Nodo("COL", col))
            if not self.esperar(")"):
                self._recuperar(); return None
            nodo.agregar(cols)
 
        if not self.esperar("valores"):
            self._recuperar(); return None
 
        # Consumir los valores entre paréntesis
        vals = Nodo("VALORES")
        if self.match("("):
            while self.actual() and self.actual().lexema != ")":
                tok = self.actual()
                if tok.lexema == ",":
                    self.avanzar(); continue
                vals.agregar(Nodo("VAL", tok.lexema))
                self.avanzar()
            if not self.esperar(")"):
                self._recuperar(); return None
        nodo.agregar(vals)
 
        if not self.esperar(";"):
            self._recuperar(); return None
        return nodo
 
    # ═══════════════════════════════════════════════════════════════════
    # BORRAR
    # ═══════════════════════════════════════════════════════════════════
    def borrar(self):
        nodo = Nodo("DELETE")
        if not self.esperar("borrar"):
            self._recuperar(); return None
        if not self.esperar("desde"):
            self._recuperar(); return None
 
        tabla = self.esperar_identificador()
        if tabla is None:
            self._recuperar(); return None
        nodo.agregar(Nodo("TABLA", tabla))
 
        if self.match("donde"):
            cond = self.condicion()
            if cond is None:
                self._recuperar(); return None
            nodo.agregar(cond)
 
        if not self.esperar(";"):
            self._recuperar(); return None
        return nodo
 
    # ═══════════════════════════════════════════════════════════════════
    # ACTUALIZAR
    # ═══════════════════════════════════════════════════════════════════
    def actualizar(self):
        nodo = Nodo("UPDATE")
        if not self.esperar("actualizar"):
            self._recuperar(); return None
 
        tabla = self.esperar_identificador()
        if tabla is None:
            self._recuperar(); return None
        nodo.agregar(Nodo("TABLA", tabla))
 
        if not self.esperar("establecer"):
            self._recuperar(); return None
 
        asignaciones = Nodo("SET")
        while True:
            col = self.esperar_identificador()
            if col is None:
                self._recuperar(); return None
            if not self.esperar("="):
                self._recuperar(); return None
            tok = self.actual()
            if not tok:
                self.errores.append((ERR_VALOR_FALTANTE,
                    "Se esperaba valor en asignación pero llegó fin de entrada"))
                return None
            asignaciones.agregar(Nodo("ASIGNACION", f"{col} = {tok.lexema}"))
            self.avanzar()
            if not self.match(","):
                break
        nodo.agregar(asignaciones)
 
        if self.match("donde"):
            cond = self.condicion()
            if cond is None:
                self._recuperar(); return None
            nodo.agregar(cond)
 
        if not self.esperar(";"):
            self._recuperar(); return None
        return nodo
 
    # ═══════════════════════════════════════════════════════════════════
    # CREAR
    # ═══════════════════════════════════════════════════════════════════
    def crear(self):
        nodo = Nodo("CREATE")
        if not self.esperar("crear"):
            self._recuperar(); return None
        if not self.esperar("tabla"):
            self._recuperar(); return None
 
        tabla = self.esperar_identificador()
        if tabla is None:
            self._recuperar(); return None
        nodo.agregar(Nodo("TABLA", tabla))
 
        # Consumir definición de columnas (todo hasta ';')
        if self.match("("):
            columnas_def = Nodo("COLUMNAS_DEF")
            while self.actual() and self.actual().lexema != ")":
                tok = self.actual()
                columnas_def.agregar(Nodo("DEF_TOKEN", tok.lexema))
                self.avanzar()
            if not self.esperar(")"):
                self._recuperar(); return None
            nodo.agregar(columnas_def)
 
        if not self.esperar(";"):
            self._recuperar(); return None
        return nodo
 
    # ═══════════════════════════════════════════════════════════════════
    # ELIMINAR
    # ═══════════════════════════════════════════════════════════════════
    def eliminar(self):
        nodo = Nodo("DROP")
        if not self.esperar("eliminar"):
            self._recuperar(); return None
        if not self.esperar("tabla"):
            self._recuperar(); return None
 
        tabla = self.esperar_identificador()
        if tabla is None:
            self._recuperar(); return None
        nodo.agregar(Nodo("TABLA", tabla))
 
        if not self.esperar(";"):
            self._recuperar(); return None
        return nodo
 
    # ═══════════════════════════════════════════════════════════════════
    # MOSTRAR
    # ═══════════════════════════════════════════════════════════════════
    def mostrar(self):
        nodo = Nodo("SHOW")
        if not self.esperar("mostrar"):
            self._recuperar(); return None
        while self.actual() and self.actual().lexema != ";":
            nodo.agregar(Nodo("ARG", self.actual().lexema))
            self.avanzar()
        if not self.esperar(";"):
            self._recuperar(); return None
        return nodo
 
    # ═══════════════════════════════════════════════════════════════════
    # USAR
    # ═══════════════════════════════════════════════════════════════════
    def usar(self):
        nodo = Nodo("USAR")
        if not self.esperar("usar"):
            self._recuperar(); return None
        nombre = self.esperar_identificador()
        if nombre is None:
            self._recuperar(); return None
        nodo.agregar(Nodo("BD", nombre))
        if not self.esperar(";"):
            self._recuperar(); return None
        return nodo
