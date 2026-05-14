# Documentación de colores — Compilador miniSQL

## Paleta de colores por tipo de token

| Grupo               | Rango de códigos | Color        | Hex       | Ejemplo de tokens                         |
|---------------------|-----------------|--------------|-----------|-------------------------------------------|
| Palabras reservadas | 1001 – 1040     | Cian         | `#4FC3F7` | `SELECCIONAR`, `DESDE`, `DONDE`, `TABLA`  |
| Operadores          | 2001 – 2010     | Naranja      | `#FFB74D` | `=`, `<>`, `<`, `>`, `+`, `-`, `*`, `/`  |
| Símbolos            | 3001 – 3005     | Amarillo     | `#FFF176` | `(`, `)`, `,`, `;`, `.`                   |
| IDENTIFICADOR       | 6000+           | Blanco       | `#FFFFFF` | nombres de tablas, columnas, alias        |
| ENTERO              | 7000+           | Verde lima   | `#AED581` | `42`, `100`, `0`                          |
| FLOTANTE            | 8000+           | Verde menta  | `#80CBC4` | `3.14`, `0.5`, `99.99`                    |
| CADENA_TEXTO        | 9000+           | Coral        | `#EF9A9A` | `'Hola'`, `'valor'`                       |
| Error léxico        | (flag de error) | Rojo         | `#FF5252` | caracteres no reconocidos, cadenas sin cerrar |

---

## Referencia completa de tokens

### Palabras reservadas (1001–1040)
| Token              | Código |
|--------------------|--------|
| USAR               | 1001   |
| CREAR              | 1002   |
| ELIMINAR           | 1003   |
| MODIFICAR          | 1004   |
| SELECCIONAR        | 1005   |
| INSERTAR           | 1006   |
| ACTUALIZAR         | 1007   |
| BORRAR             | 1008   |
| MOSTRAR            | 1009   |
| CONCEDER           | 1010   |
| REVOCAR            | 1011   |
| TABLA              | 1012   |
| BASE_DE_DATOS      | 1013   |
| BASES              | 1014   |
| USUARIO            | 1015   |
| PERFIL             | 1016   |
| ESTRUCTURA         | 1017   |
| TODO               | 1018   |
| VALORES            | 1019   |
| EN                 | 1020   |
| DESDE              | 1021   |
| DONDE              | 1022   |
| TENIENDO           | 1023   |
| LIMITE             | 1024   |
| ORDENAR            | 1025   |
| AGRUPAR            | 1026   |
| ASCENDENTE         | 1027   |
| DESCENDENTE        | 1028   |
| A                  | 1029   |
| PARA               | 1030   |
| IDENTIFICADO_POR   | 1031   |
| ENTEROS            | 1032   |
| CARACTERES         | 1033   |
| DECIMALES          | 1034   |
| NO_NULO            | 1035   |
| CONTRASEÑA         | 1036   |
| PERMISOS           | 1037   |
| TODOS_PRIVILEGIOS  | 1038   |
| Y                  | 1039   |
| O                  | 1040   |

### Operadores (2001–2010)
| Token | Código |
|-------|--------|
| =     | 2001   |
| <>    | 2002   |
| <     | 2003   |
| >     | 2004   |
| <=    | 2005   |
| >=    | 2006   |
| +     | 2007   |
| -     | 2008   |
| *     | 2009   |
| /     | 2010   |

### Símbolos (3001–3005)
| Token | Código |
|-------|--------|
| (     | 3001   |
| )     | 3002   |
| ,     | 3003   |
| ;     | 3004   |
| .     | 3005   |

### Tipos dinámicos
| Token        | Base |
|--------------|------|
| IDENTIFICADOR| 6000 |
| ENTERO       | 7000 |
| FLOTANTE     | 8000 |
| CADENA_TEXTO | 9000 |

---

## Notas de implementación

- El coloreado se aplica **tanto en el panel "Código SQL"** (coloreando directamente sobre el texto fuente usando las posiciones línea/columna del lexer) **como en el panel "Tokens"** (coloreando cada fila de la lista).
- Se usa el widget `tk.Text` subyacente de `CTkTextbox` (accesible en `._textbox`) para configurar `tag_configure` y `tag_add`, ya que `CTkTextbox` no expone tags de color de forma nativa.
- La función `color_de_token(tipo)` centraliza toda la lógica de asignación de color; modificarla es suficiente para cambiar la paleta en toda la GUI.
- Los errores léxicos tienen prioridad sobre cualquier otro rango: si `Token.es_error(tipo)` devuelve `True`, el color siempre es rojo (`#FF5252`), independientemente del código numérico.
