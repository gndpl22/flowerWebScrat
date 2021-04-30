# listado de variables usadas en flowerWebScrat

# variables de uso relacionado a sqlite3 :
db_file="flower_Buy.db"                             #nombre de base de datos
nombre_tabla_scratch = "crudo"                              # nombre de tabla almacenamiento de scratch
nombre_tabla_resumen = "resumen"

sql_crear_tabla_resumen= """CREATE TABLE `resumen` (
	id	INTEGER NOT NULL,
	nombre	TEXT,
	aparecio_fecha	TEXT,
	precio_inicial	INTEGER,
	precio_final	INTEGER,
	cantidad_requerida	INTEGER,
	cantidad_restante	INTEGER,
	esta_activo	INTEGER,
	orden_llena	INTEGER,
	minutos_restantes	INTEGER,
	fecha_envio	TEXT,
	veces_precio_modificado	INTEGER DEFAULT 0,
	PRIMARY KEY (id)
);"""



sql_crear_tabla_crudo= """CREATE TABLE `crudo` (    
	fecha_cons      TEXT NOT NULL,
	dia_cons    TEXT NOT NULL,
	hora_cons TEXT NOT NULL,
	sem_num_cons    TET NOT NULL,
	id  TEXT NOT NULL,
	nombre	TEXT NOT NULL,
	fecha_env	TEXT NOT NULL,
	unidad	TEXT NOT NULL,
	cantidad	TEXT NOT NULL,
	caja	TEXT NOT NULL,
	precio	TEXT NOT NULL,
	cajas_pedidas	TEXT NOT NULL,
	cajas_rest	TEXT NOT NULL
);"""                                               # cuando no existe tabla cruda, se crea con esta sentencia

sql_seleccionar_id_unico ='SELECT DISTINCT id FROM crudo'
sql_seleccionar_datos_iniciales= 'SELECT nombre, fecha_cons, precio, cajas_pedidas, fecha_env FROM crudo WHERE id= '


sql_insertar_tabla_crudo="""INSERT INTO crudo(fecha_cons, dia_cons, hora_cons, sem_num_cons, id, nombre, fecha_env, 
unidad, cantidad, caja, 
precio, cajas_pedidas, cajas_rest) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) """

sql_insertar_id_en_resumen="""INSERT INTO resumen(id) VALUES(?)"""

# variables usadas por selenium

url="https://www.flowerbuyer.com/grower_sign_in.asp?tf=0"   # pagina de log in de F.B


# producto:  0 -------- All Groups --------
# producto:  36 Calla Lily Mini
# producto:  147 Larkspur
# producto:  155 Liatris
# producto:  164 Lisianthus Double
# producto:  217 Ranunculus
# producto:  245 Sunflower
variedad='245'                                             # dentro de pagina usado para filtrar productos

