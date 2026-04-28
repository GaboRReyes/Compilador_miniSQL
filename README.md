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
Actualmente, el sistema incluye la <strong>fase de análisis léxico</strong> y una <strong>interfaz gráfica (GUI)</strong>
que permite interactuar con el compilador de manera visual.
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
<td>Interfaz gráfica (GUI)</td>
<td>████████░░ 80%</td>
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

<h2>Interfaz gráfica (GUI)</h2>

<p>
Se implementó una interfaz moderna utilizando <strong>CustomTkinter</strong>, con estilo oscuro tipo IDE.
</p>

<ul>
<li>Editor de entrada con placeholder dinámico</li>
<li>Botón para ejecutar consultas manuales</li>
<li>Carga de archivos desde el explorador del sistema</li>
<li>Consola de entrada/salida</li>
<li>Diseño limpio con organización por contenedores</li>
</ul>

<hr>

<h2>Características de la GUI</h2>

<ul>
<li>Modo oscuro configurable</li>
<li>Botones con esquinas redondeadas</li>
<li>Interacción mediante eventos (FocusIn / FocusOut)</li>
<li>Simulación de placeholder en campos de texto</li>
<li>Integración directa con el analizador léxico</li>
</ul>

<hr>

<h2>Carga de archivos</h2>

<p>
El sistema permite seleccionar archivos desde el explorador del sistema operativo:
</p>

<ul>
<li>Soporte para archivos <code>.sql</code></li>
<li>Soporte para archivos <code>.txt</code></li>
<li>Lectura de ruta del archivo seleccionado</li>
<li>Preparado para integración con el análisis del compilador</li>
</ul>

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
Entrada (GUI o archivo)
        │
        ▼
Interfaz gráfica (CustomTkinter)
        │
        ▼
Analizador léxico (lexer.py)
        │
        ▼
Tokens + errores + tabla de símbolos
</pre>

<hr>

<h2>Estructura del proyecto</h2>

<pre>
proyecto/
├── lexer.py
├── main.py
├── GUI.py
├── entrada.sql
└── README.md
</pre>

<hr>

<h2>Ejecución</h2>

<h3>Modo consola</h3>
<pre><code>python main.py</code></pre>

<h3>Modo interfaz gráfica</h3>
<pre><code>python GUI.py</code></pre>

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
<li>CustomTkinter (interfaz gráfica)</li>
<li>Programación orientada a objetos</li>
<li>Fundamentos de compiladores</li>
</ul>

<hr>

<h2>Autor</h2>

<p>Gabriel Josafat Ramírez Reyes</p>

<hr>

<h2>Proyección</h2>

<ul>
<li>Integración completa GUI + análisis léxico</li>
<li>Análisis sintáctico</li>
<li>Análisis semántico</li>
<li>Resaltado de sintaxis en el editor</li>
<li>Consola interactiva tipo IDE</li>
</ul>

<hr>

<h2>Traducción MiniSQL → SQL</h2>

<p>
El sistema incluye un traductor que convierte instrucciones escritas en español (MiniSQL)
a sentencias SQL estándar compatibles con MySQL.
</p>

<h3>Ejemplo</h3>

<pre><code>
SELECCIONAR * DESDE alumnos DONDE edad > 18;
</code></pre>

<p><strong>Se traduce a:</strong></p>

<pre><code>
SELECT * FROM alumnos WHERE edad > 18;
</code></pre>

<h3>Características del traductor</h3>

<ul>
<li>Uso de diccionario de equivalencias</li>
<li>Tokenización con expresiones regulares</li>
<li>Conversión de palabras reservadas</li>
<li>Limpieza de espacios y sintaxis final</li>
</ul>