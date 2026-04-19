<h1 align="center">Compilador MiniSQL en Español</h1>

<p align="center">
  <strong>Tecnológico Nacional de México — Instituto Tecnológico de Celaya</strong><br>
  Lenguajes y Autómatas II
</p>

<hr>

<h2>Descripción</h2>

<p>
Este proyecto implementa un compilador para un lenguaje tipo SQL en español denominado <strong>MiniSQL</strong>.
El desarrollo sigue la arquitectura clásica de compiladores, separando cada una de sus fases.
</p>

<p>
Actualmente, el sistema incluye la <strong>fase de análisis léxico</strong>, encargada de identificar tokens,
detectar errores léxicos y construir la tabla de símbolos a partir del código fuente.
</p>

<hr>

<h2>Estado del proyecto</h2>

<table>
<tr>
<th>Fase</th>
<th>Progreso</th>
</tr>
<tr>
<td>Análisis léxico</td>
<td>██████████ 100%</td>
</tr>
<tr>
<td>Análisis sintáctico</td>
<td>░░░░░░░░░░ 0%</td>
</tr>
<tr>
<td>Análisis semántico</td>
<td>░░░░░░░░░░ 0%</td>
</tr>
<tr>
<td>Generación de código</td>
<td>░░░░░░░░░░ 0%</td>
</tr>
</table>

<hr>

<h2>Análisis léxico</h2>

<ul>
<li>Reconocimiento de palabras reservadas en español</li>
<li>Identificación de:
  <ul>
    <li>Identificadores</li>
    <li>Números enteros y flotantes</li>
    <li>Cadenas de texto</li>
  </ul>
</li>
<li>Manejo de operadores relacionales y aritméticos</li>
<li>Soporte para comentarios tipo SQL (-- comentario)</li>
<li>Detección de errores léxicos</li>
<li>Construcción de tabla de símbolos</li>
</ul>

<hr>

<h2>Flujo de procesamiento</h2>

<pre>
Código fuente (entrada.sql)
            │
            ▼
   Analizador léxico (lexer.py)
            │
            ▼
  Lista de tokens + errores
            │
            ▼
     Tabla de símbolos
</pre>

<hr>

<h2>Estructura del proyecto</h2>

<pre>
proyecto/
├── lexer.py
├── main.py
├── entrada.sql
└── README.md
</pre>

<hr>

<h2>Ejecución</h2>

<pre><code>python main.py</code></pre>

<p>El programa procesa automáticamente el archivo <code>entrada.sql</code>.</p>

<hr>

<h2>Archivo de prueba</h2>

<pre><code class="language-sql">
-- Archivo de prueba MiniSQL en Español

SELECCIONAR nombre, edad DESDE alumnos DONDE edad > 18;

INSERTAR EN clientes VALORES ('Juan', 25, 1500.50);

CREAR TABLA productos (
    id ENTEROS NO_NULO,
    precio DECIMALES,
    descripcion CARACTERES
);

ACTUALIZAR inventario DONDE id = 7;

BORRAR DESDE pedidos DONDE id = 3;

MOSTRAR BASES;
USAR tienda_db;

SELECCIONAR * DESDE ventas
DONDE monto >= 100.50 Y categoria = 'ropa'
ORDENAR ASCENDENTE LIMITE 5;

-- Errores léxicos
SELECCIONAR 94.15.12;
SELECCIONAR 123abc;
SELECCIONAR 'cadena sin cerrar;
</code></pre>

<hr>

<h2>Salida del sistema</h2>

<ul>
<li>Lista de tokens (tipo, lexema, posición)</li>
<li>Reporte de errores léxicos</li>
<li>Tabla de símbolos</li>
<li>Resumen de ejecución</li>
</ul>

<hr>

<h2>Manejo de errores</h2>

<pre>
Número inválido        → 94.15.12
Identificador inválido → 123abc
Cadena sin cerrar      → 'texto
Carácter desconocido   → @
</pre>

<hr>

<h2>Tecnologías</h2>

<ul>
<li>Python 3</li>
<li>Programación orientada a objetos</li>
<li>Fundamentos de compiladores</li>
</ul>

<hr>

<h2>Autor</h2>

<p>Gabriel Josafat Ramírez Reyes</p>

<hr>

<h2>Proyección</h2>

<ul>
<li>Análisis sintáctico</li>
<li>Análisis semántico</li>
<li>Generación de código intermedio</li>
</ul>
