-- Archivo de prueba MiniSQL en Español

-- Consulta simple
SELECCIONAR nombre, edad DESDE alumnos DONDE edad > 18;

-- Inserción
INSERTAR EN clientes VALORES ('Juan', 25, 1500.50);

-- Crear tabla
CREAR TABLA productos (
    id ENTEROS NO_NULO,
    precio DECIMALES,
    descripcion CARACTERES
);

-- Actualizar registros
ACTUALIZAR inventario DONDE id = 7;

-- Borrar
BORRAR DESDE pedidos DONDE id = 3;

-- Mostrar y Usar
MOSTRAR BASES;
USAR tienda_db;

-- Con operadores Y / O
SELECCIONAR * DESDE ventas
DONDE monto >= 100.50 Y categoria = 'ropa'
ORDENAR ASCENDENTE LIMITE 5;

-- Errores léxicos intencionales
SELECCIONAR 94.15.12;
SELECCIONAR 123abc;
SELECCIONAR 'cadena sin cerrar;
