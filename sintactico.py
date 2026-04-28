from lexer import Token

#===NODO DEL ÁRBOL===#
class Nodo:
    def __init__(self, tipo, valor=None):
        self.tipo = tipo #tipo de nodo (ej: SELECT, TABLA, CONDICION)
        self.valor = valor #valor asociado (ej: nombre de tabla, columna, etc)
        self.hijos = [] #lista de nodos hijos
    #===AGREGAR HIJO (CREACIÓN DE ARBOL)===#
    def agregar(self, nodo):
        if nodo:  
            self.hijos.append(nodo)

#===ANALIZADOR SINTÁCTICO===#
class AnalizadorSintactico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.errores = []

    def actual(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def avanzar(self):
        self.i += 1

    def match(self, palabra):
        tok = self.actual()
        if tok and tok.lexema.lower() == palabra.lower():
            self.avanzar()
            return True
        return False

    def esperar(self, palabra):
        tok = self.actual()

        if not tok:
            self.errores.append(f"Se esperaba '{palabra}' pero llegó fin de entrada")
            return False

        if tok.lexema.lower() != palabra.lower():
            self.errores.append(
                f"Se esperaba '{palabra}' pero llegó '{tok.lexema}'"
            )
            return False

        self.avanzar()
        return True

    def esperar_identificador(self):
        tok = self.actual()

        if tok and Token.nombre(tok.tipo) == "IDENTIFICADOR":
            self.avanzar()
            return tok.lexema

        self.errores.append("Se esperaba un IDENTIFICADOR")
        return None
    #===INICIO===#

    def analizar(self):
        arbol = []

        while self.actual() is not None:
            nodo = self.sentencia()
            if nodo is None:
                return None
            arbol.append(nodo)

        return arbol


    def sentencia(self):
        tok = self.actual()
        if not tok:
            return None

        palabra = tok.lexema.lower()

        reglas = {
            "usar": self.usar,
            "seleccionar": self.seleccionar,
            "insertar": self.insertar,
            "borrar": self.borrar,
            "crear": self.crear,
            "eliminar": self.eliminar,
            "mostrar": self.mostrar,
            "actualizar": self.actualizar
        }

        if palabra in reglas:
            return reglas[palabra]()

        self.errores.append(f"Sentencia no válida: '{tok.lexema}'")
        self.avanzar()
        return None

    # =========================
    # REGLAS
    # =========================

    def usar(self):
        nodo = Nodo("USAR")

        if not self.esperar("usar"):
            return None

        nombre = self.esperar_identificador()
        if not nombre:
            return None

        if not self.esperar(";"):
            return None

        nodo.agregar(Nodo("BD", nombre))
        return nodo
    
    def actualizar(self):
        nodo = Nodo("UPDATE")

        if not self.esperar("actualizar"):
            return None

        tabla = self.esperar_identificador()
        if not tabla:
            return None

        nodo.agregar(Nodo("TABLA", tabla))

        if not self.esperar("establecer"):
            return None

        asignaciones = Nodo("SET")

        while True:
            col = self.esperar_identificador()
            if not col:
                return None

            if not self.esperar("="):
                return None

            tok = self.actual()
            if not tok:
                self.errores.append("Se esperaba un valor")
                return None

            asignaciones.agregar(Nodo("ASIGNACION", f"{col} = {tok.lexema}"))
            self.avanzar()

            if not self.match(","):
                break

        nodo.agregar(asignaciones)

        if self.match("donde"):
            cond = self.condicion()
            if not cond:
                return None
            nodo.agregar(cond)

        if not self.esperar(";"):
            return None

        return nodo

    def seleccionar(self):
        nodo = Nodo("SELECT")

        if not self.esperar("seleccionar"):
            return None

        if self.match("todo"):
            nodo.agregar(Nodo("COLUMNAS", "*"))
        else:
            col = self.esperar_identificador()
            if not col:
                return None
            nodo.agregar(Nodo("COLUMNAS", col))

        if not self.esperar("desde"):
            return None

        tabla = self.esperar_identificador()
        if not tabla:
            return None

        nodo.agregar(Nodo("TABLA", tabla))

        if self.match("donde"):
            cond = self.condicion()
            if not cond:
                return None
            nodo.agregar(cond)

        if not self.esperar(";"):
            return None

        return nodo


    def insertar(self):
        nodo = Nodo("INSERT")

        if not self.esperar("insertar"):
            return None

        if not self.esperar("en"):
            return None

        tabla = self.esperar_identificador()
        if not tabla:
            return None

        nodo.agregar(Nodo("TABLA", tabla))

        if self.match("("):
            while self.actual() and self.actual().lexema != ")":
                self.avanzar()
            if not self.esperar(")"):
                return None

        if not self.esperar("valores"):
            return None

        while self.actual() and self.actual().lexema != ";":
            self.avanzar()

        if not self.esperar(";"):
            return None

        return nodo


    def borrar(self):
        nodo = Nodo("DELETE")

        if not self.esperar("borrar"):
            return None

        if not self.esperar("desde"):
            return None

        tabla = self.esperar_identificador()
        if not tabla:
            return None

        nodo.agregar(Nodo("TABLA", tabla))

        if self.match("donde"):
            cond = self.condicion()
            if not cond:
                return None
            nodo.agregar(cond)

        if not self.esperar(";"):
            return None

        return nodo


    def crear(self):
        nodo = Nodo("CREATE")

        if not self.esperar("crear"):
            return None

        if not self.esperar("tabla"):
            return None

        tabla = self.esperar_identificador()
        if not tabla:
            return None

        nodo.agregar(Nodo("TABLA", tabla))

        while self.actual() and self.actual().lexema != ";":
            self.avanzar()

        if not self.esperar(";"):
            return None

        return nodo


    def eliminar(self):
        nodo = Nodo("DROP")

        if not self.esperar("eliminar"):
            return None
        
        if not self.esperar("tabla"):
            return None

        tabla = self.esperar_identificador()
        if not tabla:
            return None

        nodo.agregar(Nodo("TABLA", tabla))

        if not self.esperar(";"):
            return None

        return nodo


    def mostrar(self):
        nodo = Nodo("SHOW")

        if not self.esperar("mostrar"):
            return None

        while self.actual() and self.actual().lexema != ";":
            self.avanzar()

        if not self.esperar(";"):
            return None

        return nodo


    def condicion(self):
        nodo = Nodo("CONDICION")

        col = self.esperar_identificador()
        if not col:
            return None

        nodo.agregar(Nodo("COLUMNA", col))

        tok = self.actual()
        if not tok:
            self.errores.append("Se esperaba operador")
            return None

        nodo.agregar(Nodo("OPERADOR", tok.lexema))
        self.avanzar()

        tok = self.actual()
        if not tok:
            self.errores.append("Se esperaba valor")
            return None

        nodo.agregar(Nodo("VALOR", tok.lexema))
        self.avanzar()

        return nodo