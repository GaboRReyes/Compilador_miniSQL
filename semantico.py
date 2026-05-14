from lexer import Token
 
# ── Códigos de error semántico ────────────────────────────────────────────────
ERR_SEM_TABLA_DESCONOCIDA   = -20
ERR_SEM_COLUMNA_DESCONOCIDA = -21
ERR_SEM_TIPO_INCOMPATIBLE   = -22
ERR_SEM_LIMITE_INVALIDO     = -23
ERR_SEM_SIN_COLUMNAS        = -24
ERR_SEM_VALORES_DESBALANCE  = -25
ERR_SEM_OP_LOGICO_INVALIDO  = -26
ERR_SEM_CONDICION_VACIA     = -27
 
# Tipos numéricos aceptados para comparaciones numéricas
_TIPOS_NUMERICOS = {"ENTEROS", "DECIMALES", "ENTERO", "FLOTANTE"}
_TIPOS_TEXTO     = {"CARACTERES", "CADENA_TEXTO"}
 
 
class AnalizadorSemantico:
 
    def __init__(self, arbol, esquema=None):
        """
        arbol   : lista de Nodo devuelta por AnalizadorSintactico.analizar()
        esquema : dict { nombre_tabla: { nombre_col: tipo_col } } (opcional)
        """
        self.arbol   = arbol if arbol else []
        self.esquema = esquema or {}
        self.errores = []    # lista de tuplas (codigo, mensaje)
        self.avisos  = []    # advertencias no fatales
 
    # ── API pública ───────────────────────────────────────────────────────────
    def analizar(self):
        """Recorre el árbol y ejecuta todas las verificaciones semánticas."""
        for nodo in self.arbol:
            self._verificar_sentencia(nodo)
        return len(self.errores) == 0
 
    def reporte(self):
        lineas = ["\n------ ANÁLISIS SEMÁNTICO ----------------------------------"]
        if not self.errores and not self.avisos:
            lineas.append("  OK — Sin errores semánticos.")
        else:
            for cod, msg in self.errores:
                lineas.append(f"  ERROR [{cod}]: {msg}")
            for msg in self.avisos:
                lineas.append(f"  AVISO: {msg}")
        lineas.append("-----------------------------------------------------------")
        return "\n".join(lineas)
 
    # ── Dispatcher ────────────────────────────────────────────────────────────
    def _verificar_sentencia(self, nodo):
        handlers = {
            "SELECT": self._chk_select,
            "INSERT": self._chk_insert,
            "DELETE": self._chk_delete,
            "UPDATE": self._chk_update,
            "CREATE": self._chk_crear,
            "DROP":   self._chk_drop,
            "USAR":   self._chk_usar,
            "SHOW":   lambda n: None,   # nada que verificar
        }
        fn = handlers.get(nodo.tipo)
        if fn:
            fn(nodo)
        else:
            self.avisos.append(f"Nodo de tipo '{nodo.tipo}' no verificado semánticamente.")
 
    # ── Helpers ───────────────────────────────────────────────────────────────
    def _obtener_hijo(self, nodo, tipo):
        """Devuelve el primer hijo con el tipo indicado, o None."""
        for h in nodo.hijos:
            if h.tipo == tipo:
                return h
        return None
 
    def _obtener_hijos(self, nodo, tipo):
        return [h for h in nodo.hijos if h.tipo == tipo]
 
    def _nombre_tabla(self, nodo):
        h = self._obtener_hijo(nodo, "TABLA")
        return h.valor if h else None
 
    def _verificar_tabla_existe(self, tabla):
        if not self.esquema:
            return True   # modo permisivo
        if tabla not in self.esquema:
            self.errores.append((ERR_SEM_TABLA_DESCONOCIDA,
                f"La tabla '{tabla}' no existe en el esquema."))
            return False
        return True
 
    def _verificar_columna(self, tabla, columna):
        if not self.esquema or tabla not in self.esquema:
            return True   # modo permisivo
        if columna == "*":
            return True
        cols = self.esquema[tabla]
        if columna not in cols:
            self.errores.append((ERR_SEM_COLUMNA_DESCONOCIDA,
                f"La columna '{columna}' no existe en la tabla '{tabla}'."))
            return False
        return True
 
    def _tipo_col(self, tabla, columna):
        """Devuelve el tipo declarado de una columna, o None si no está en esquema."""
        if not self.esquema or tabla not in self.esquema:
            return None
        return self.esquema[tabla].get(columna)
 
    # ── Verificación de condiciones ───────────────────────────────────────────
    def _verificar_condicion(self, nodo_cond, tabla):
        """
        nodo_cond.tipo == "CONDICION"
        Sus hijos son una mezcla de COND_SIMPLE y OP_LOGICO.
        Reglas:
          - Al menos una COND_SIMPLE debe existir.
          - No puede haber dos OP_LOGICO consecutivos.
          - No puede empezar ni terminar con OP_LOGICO.
          - Cada COND_SIMPLE: columna existe, tipos compatibles.
        """
        if not nodo_cond:
            return
 
        hijos = nodo_cond.hijos
        if not hijos:
            self.errores.append((ERR_SEM_CONDICION_VACIA,
                "La cláusula DONDE está vacía."))
            return
 
        # Verificar alternancia OP_LOGICO / COND_SIMPLE
        prev_tipo = None
        for h in hijos:
            if h.tipo == "OP_LOGICO":
                if prev_tipo is None or prev_tipo == "OP_LOGICO":
                    self.errores.append((ERR_SEM_OP_LOGICO_INVALIDO,
                        f"Operador lógico '{h.valor}' mal ubicado en la condición."))
            elif h.tipo == "COND_SIMPLE":
                self._verificar_cond_simple(h, tabla)
            prev_tipo = h.tipo
 
        if prev_tipo == "OP_LOGICO":
            self.errores.append((ERR_SEM_OP_LOGICO_INVALIDO,
                "La condición termina con un operador lógico Y/O sin condición derecha."))
 
    def _verificar_cond_simple(self, nodo, tabla):
        col_nodo = self._obtener_hijo(nodo, "COLUMNA")
        op_nodo  = self._obtener_hijo(nodo, "OPERADOR")
        val_nodo = self._obtener_hijo(nodo, "VALOR")
 
        if not col_nodo or not op_nodo or not val_nodo:
            self.errores.append((ERR_SEM_CONDICION_VACIA,
                "Condición incompleta (falta columna, operador o valor)."))
            return
 
        columna = col_nodo.valor
        valor   = val_nodo.valor
 
        # Verificar que la columna exista
        self._verificar_columna(tabla, columna)
 
        # Verificar compatibilidad de tipos (solo si hay esquema)
        tipo_col = self._tipo_col(tabla, columna)
        if tipo_col:
            es_cadena_valor = valor.startswith("'") and valor.endswith("'")
            es_numerico_valor = not es_cadena_valor
 
            if tipo_col in _TIPOS_NUMERICOS and es_cadena_valor:
                self.errores.append((ERR_SEM_TIPO_INCOMPATIBLE,
                    f"Columna '{columna}' es numérica ({tipo_col}) "
                    f"pero se compara con cadena '{valor}'."))
            elif tipo_col in _TIPOS_TEXTO and es_numerico_valor:
                # Podría ser un identificador → aviso, no error fatal
                self.avisos.append(
                    f"Columna '{columna}' es texto ({tipo_col}) "
                    f"pero el valor '{valor}' no es una cadena entre comillas.")
 
    # ── Sentencias individuales ───────────────────────────────────────────────
    def _chk_select(self, nodo):
        tabla = self._nombre_tabla(nodo)
        if not tabla:
            return
 
        self._verificar_tabla_existe(tabla)
 
        # Verificar columnas listadas
        cols_nodo = self._obtener_hijo(nodo, "COLUMNAS")
        if cols_nodo:
            col_hijos = self._obtener_hijos(cols_nodo, "COL")
            if not col_hijos:
                self.errores.append((ERR_SEM_SIN_COLUMNAS,
                    "SELECT no tiene columnas definidas."))
            else:
                for ch in col_hijos:
                    self._verificar_columna(tabla, ch.valor)
        else:
            self.errores.append((ERR_SEM_SIN_COLUMNAS,
                "SELECT no tiene cláusula de columnas."))
 
        # Verificar condición DONDE
        cond_nodo = self._obtener_hijo(nodo, "CONDICION")
        self._verificar_condicion(cond_nodo, tabla)
 
        # Verificar LIMITE
        lim_nodo = self._obtener_hijo(nodo, "LIMITE")
        if lim_nodo:
            try:
                val = int(lim_nodo.valor)
                if val <= 0:
                    self.errores.append((ERR_SEM_LIMITE_INVALIDO,
                        f"LIMITE debe ser un entero positivo, se recibió '{lim_nodo.valor}'."))
            except (ValueError, TypeError):
                self.errores.append((ERR_SEM_LIMITE_INVALIDO,
                    f"LIMITE '{lim_nodo.valor}' no es un entero válido."))
 
    def _chk_insert(self, nodo):
        tabla = self._nombre_tabla(nodo)
        if tabla:
            self._verificar_tabla_existe(tabla)
 
        cols_nodo = self._obtener_hijo(nodo, "COLUMNAS")
        vals_nodo = self._obtener_hijo(nodo, "VALORES")
 
        if cols_nodo and vals_nodo:
            n_cols = len(self._obtener_hijos(cols_nodo, "COL"))
            n_vals = len(self._obtener_hijos(vals_nodo, "VAL"))
            if n_cols != n_vals:
                self.errores.append((ERR_SEM_VALORES_DESBALANCE,
                    f"INSERT: se declararon {n_cols} columnas pero se dieron {n_vals} valores."))
 
        # Verificar columnas contra esquema
        if cols_nodo and tabla:
            for ch in self._obtener_hijos(cols_nodo, "COL"):
                self._verificar_columna(tabla, ch.valor)
 
    def _chk_delete(self, nodo):
        tabla = self._nombre_tabla(nodo)
        if tabla:
            self._verificar_tabla_existe(tabla)
 
        cond_nodo = self._obtener_hijo(nodo, "CONDICION")
        if not cond_nodo:
            self.avisos.append(
                f"DELETE sobre '{tabla}' sin cláusula DONDE — "
                "eliminará TODOS los registros.")
        else:
            self._verificar_condicion(cond_nodo, tabla)
 
    def _chk_update(self, nodo):
        tabla = self._nombre_tabla(nodo)
        if tabla:
            self._verificar_tabla_existe(tabla)
 
        set_nodo = self._obtener_hijo(nodo, "SET")
        if set_nodo and tabla and self.esquema:
            for asig in self._obtener_hijos(set_nodo, "ASIGNACION"):
                # asig.valor es "col = valor"
                partes = asig.valor.split("=", 1)
                if len(partes) == 2:
                    col = partes[0].strip()
                    self._verificar_columna(tabla, col)
 
        cond_nodo = self._obtener_hijo(nodo, "CONDICION")
        if not cond_nodo:
            self.avisos.append(
                f"UPDATE sobre '{tabla}' sin cláusula DONDE — "
                "actualizará TODOS los registros.")
        else:
            self._verificar_condicion(cond_nodo, tabla)
 
    def _chk_crear(self, nodo):
        tabla = self._nombre_tabla(nodo)
        if tabla and self.esquema and tabla in self.esquema:
            self.avisos.append(
                f"CREATE TABLE '{tabla}': la tabla ya existe en el esquema.")
 
    def _chk_drop(self, nodo):
        tabla = self._nombre_tabla(nodo)
        if tabla:
            self._verificar_tabla_existe(tabla)
 
    def _chk_usar(self, nodo):
        bd_nodo = self._obtener_hijo(nodo, "BD")
        if bd_nodo:
            self.avisos.append(f"Usando base de datos: '{bd_nodo.valor}'.")
