import sqlite3


def db_obtener_cursor (db_nombre):
    print("en db_obtener_cursor>",db_nombre)
    conn = sqlite3.connect(db_nombre) # crear coneccion
    cur = conn.cursor() # crear cursor
    return (conn,cur)

def db_existe_tabla (cursor,tb_nombre):             # comprovar si existe la tabla
    cursor.execute("SELECT name FROM sqlite_master "
                    "WHERE type='table' "
                    "AND name=?", (tb_nombre,))  # buscar tabla crudo
    existencia = cursor.fetchall() # recuperar objeos encontrados

    if existencia :                     # verificar si existe la tabla
        print("DB_EXISTE_TABLA >> si hay tabla:",tb_nombre)
        return (True)
    else:                               # si no existe informar y crear tabla crudo
        print("DB_EXISTE_TABLA >> no hay tabla:",tb_nombre)
        return (False)

def db_ejecutar (cursor,instruccion,*args):            # crea una tabla nueva
    try:
        if args :
            # print(*args)
            cursor.execute(instruccion,*args)


        else:
            cursor.execute(instruccion)

    except sqlite3.Error as e:
        print(e)

def db_cerrar (conn):
    conn.close()


def iniciar (db,tabla,instrucciones_creado,V=0):

    if V : print("en db. iniciar:",db,tabla,instrucciones_creado)
    try:
        cursor = db_obtener_cursor(db)
        if V==1: print("conectado a bd:",db)
        if V==1 : print("cursor obtenido", cursor)
        if db_existe_tabla(cursor[1],tabla):
            if V==1 : print("tabla accedida")
            return cursor
        else:
            if V==1 :print("tabla no existe")
            db_ejecutar(cursor[1],instrucciones_creado)
            if V==1: print("tabla:",tabla,"fue creada exitosamente !")
            return cursor
    except:
            return False


