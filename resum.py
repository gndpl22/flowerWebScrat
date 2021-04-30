import database
import variables
import sqlite3
# from datetime import datetime
import datetime

#//////////////////////////////////////////FUNCIONES//////////////////////////////////////////////////////////
def diferencia_tiempo_consulta_vencimiento(fecha_cons, hora_cons, fecha_env):
    fecha_mas_hora_consulta = fecha_cons + ' ' + hora_cons
    fecha_y_hora_consulta = datetime.datetime.strptime(str(fecha_mas_hora_consulta), '%Y-%m-%d %H:%M')
    fecha_mas_hora_envio = fecha_env + ' 14:00'
    fecha_y_hora_envio = datetime.datetime.strptime(str(fecha_mas_hora_envio), '%b %d %Y %H:%M')
    tiempo_diferencia = fecha_y_hora_envio - fecha_y_hora_consulta
    tiempo_diferencia_minutos = int((tiempo_diferencia.total_seconds()) / 60)
    return (tiempo_diferencia_minutos)


#/////////////////////////////////////////////////  FIN DE FUNCIONES  //////////////////////////////////////////////////

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#                               PASO 1 : Generar y llenar tabla resumen con datos de arranque

# copiar id, nombre, fecha aparicion, precio inicial, cantidad requerida, fecha de envio  de orden de tabla cruda a
#     resumen si es que no existe en tabla resumen

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

print("-------------------PASO 1-------------------")
print("generando id de tabla resumen ")
cur=database.iniciar(variables.db_file,variables.nombre_tabla_resumen,variables.sql_crear_tabla_resumen)
# print(cur)
# cur[1].execute('SELECT name from sqlite_master where type="table"')
# print(cur[1].fetchall())

#
# cur[1].execute('SELECT id from resumen')
# existencias_tabla_resumen = cur[1].fetchall()
# print(existencias_tabla_resumen)

# for id in existencias_tabla_resumen:
cur[1].execute('SELECT DISTINCT id '
               'FROM crudo '
               'WHERE crudo.id NOT IN (SELECT id from resumen)'
               'ORDER BY id ASC')
resultados= cur[1].fetchall()
# print(resultados)
for id in resultados:
    # print(id)
    sentencia='SELECT id, nombre, fecha_cons, precio, cajas_pedidas, fecha_env, cajas_rest ' \
              'FROM crudo ' \
              'WHERE crudo.id='+str(*id)+' ORDER BY rowid ASC'
    cur[1].execute(sentencia)
    res=cur[1].fetchone()
    insertar='INSERT INTO resumen (id, nombre, aparecio_fecha, precio_inicial, cantidad_requerida, fecha_envio, ' \
             'cantidad_restante) ' \
             'values '+str(res)+';'

    cur[1].execute(insertar)
    cur[0].commit()
    # print(insertar)

print("---------------FIN PASO 1-------------------")

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#                                                       PASO 2:

#        llenar en tabla resumen precio_final con precio_inicial si es que el campo tiene valor inexistente

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

print("-------------------PASO 2-------------------")
print("llenando datos nuevos en  tabla resumen ")


cur[1].execute('SELECT id, precio_inicial, precio_final FROM resumen')
seleccion = cur[1]. fetchall()
# print(seleccion)
for id in seleccion:
    if id[2] == None:
        sentencia="UPDATE resumen SET precio_final ='"+str(id[1])+"' WHERE id="+str(id[0])+";"
        # print(sentencia)
        cur[1].execute(sentencia)
cur[0].commit()
print("---------------FIN PASO 2-------------------")

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#                            paso 3 : crear tabla de cambio de precio  y llenarla
#

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

print("-------------------PASO 3-------------------")
print("generando tabla cambio precios ")

if not database.db_existe_tabla(cur[1],'cambio_precio'):
    print("no existe tabla cambio_precio")
    cur[1].execute("""CREATE TABLE `cambio_precio` (
	id	INTEGER,
	fecha_cambio_precio	TEXT,
	hora_cambio_precio	TEXT,
	precio_anterior	INTEGER,
	precio_nuevo	INTEGER,
	referencia_rowid_tc INTEGER,
	tiempo_falta_vencimiento_m INTEGE,
	FOREIGN KEY(`id`) REFERENCES `resumen`(`id`)
);""")

cur[1].execute('SELECT id FROM resumen')    #para el id en la tabla resumen
resultado= cur[1].fetchall()

for id in resultado:            # para cada id de la tabla resumen
    row='SELECT precio_nuevo, referencia_rowid_tc, rowid FROM cambio_precio WHERE id = '+str(*id)+' ORDER BY ' \
                                                                                           'cambio_precio.rowid DESC'
    # print(row)
    cur[1].execute(row)

    ultima_linea_conocida = cur[1].fetchone()   #seleccionar precio_nuevo, referencia de rowid de tc
                                                # de el ultimo registro disponible en tabla cambio_precio
    # print("el id:",id, "de ultima linea conocida:", ultima_linea_conocida)
    if ultima_linea_conocida == None :          # si el registro esta vacio
        print(id,"sin registro previo, generando")

        valores='SELECT rowid, fecha_cons, hora_cons, precio, fecha_env FROM crudo WHERE id = '+str(*id)+' ' \
                 'ORDER BY crudo.rowid ASC'

        cur[1].execute(valores)
        datos = cur[1].fetchone()           # seleccionar el primer registro para el id :rowid, fecha_cons, hora_cons,
                                            # precio, fecha_env
                                            # de tabla crudo

        # calcular tiempo restante en minutos para que se cierre el id
        diferencia=diferencia_tiempo_consulta_vencimiento(datos[1],datos[2],datos[4])

        resp = (str(*id),str(datos[1]),str(datos[2]),'0',str(datos[3]),str(datos[0]),str(diferencia))

        insertar = 'INSERT INTO cambio_precio (id, fecha_cambio_precio, hora_cambio_precio, precio_anterior, ' \
                   'precio_nuevo, referencia_rowid_tc, tiempo_falta_vencimiento_m) ' \
                   'values ' + str(resp) + ';'

        cur[1].execute(insertar)        # inserar el primer registro para el id # en la tabla cambio_precio

        # insertar en tabla resumen la primera acualizacion de minutos restantes
        # insertar2="UPDATE resumen SET minutos_restantes ="+str(diferencia)+" WHERE id="+str(*id)+";"

        # cur[1].execute(insertar2)
        # cur[0].commit()

        # insertar en la tabla resumen la cantidad conseguida inicial

    else:   # si es que si existe registro para el id en la tabla cambio_precio
        # print("con registro previo")

        valores = 'SELECT rowid, fecha_cons, hora_cons, precio, fecha_env ' \
                  'FROM crudo ' \
                  'WHERE id = ' + str(*id) + ' ' \
                  'AND rowid > '+str(ultima_linea_conocida[1])+' ' \
                  'AND precio NOT LIKE "'+str(ultima_linea_conocida[0])+'%" ' \
                  'ORDER BY crudo.rowid ASC'

        # print(valores)
        cur[1].execute(valores)
        datos=cur[1].fetchone()

        if datos != None:
            # print("se detecto incremento de precio en el id:",*id,"cambio a precio:",datos)
            diferencia = diferencia_tiempo_consulta_vencimiento(datos[1], datos[2], datos[4])
            # print("precio anterior",ultima_linea_conocida[0])
            # print("nuevo precio",datos[3])

            resp = (str(*id),str(datos[1]),str(datos[2]),str(ultima_linea_conocida[0]),str(datos[3]),str(datos[0]),
                    str(diferencia))


            insertar = 'INSERT INTO cambio_precio (id, fecha_cambio_precio, hora_cambio_precio, precio_anterior, ' \
                       'precio_nuevo, referencia_rowid_tc, tiempo_falta_vencimiento_m) ' \
                       'values ' + str(resp) + ';'

            cur[1].execute(insertar)        # inserar el primer registro para el id # en la tabla cambio_precio

            mod = 'UPDATE resumen SET precio_final='+str(datos[3])+',veces_precio_modificado = veces_precio_modificado+1 ' \
                  'WHERE id='+str(*id)+';'
            # print(mod)
            cur[1].execute(str(mod))
cur[0].commit()
print("---------------FIN PASO 3-------------------")


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#                                paso 4 : crear base de datos de ventas y llenarla

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# 4.1 : crear tabla ventas si no existe
print("-------------------PASO 4-------------------")
print("generando tabla ventas (aumento o disminucion de pedidos) ")


if not database.db_existe_tabla(cur[1],'ventas'):
    print("no existe tabla ventas")
    cur[1].execute("""CREATE TABLE `ventas` (
	id	INTEGER,
	fecha_venta	TEXT,
	hora_venta	TEXT,
	precio_venta	INTEGER,
	cantidad_vendida	INTEGER,
	cantidad_agregada   INTEGER,
	ref_rowid_tc INTEGER,
	tiempo_faltante	TEXT,
	FOREIGN KEY(`id`) REFERENCES `resumen`(`id`)
);""")

# 4.2 llenar datos iniciales desde tabla resumen

cur[1].execute('SELECT id, cantidad_requerida ,cantidad_restante FROM resumen')    #para el id en la tabla
# resumen
resultado= cur[1].fetchall()

for id in resultado :
    #seleccionar ultima linea de registro conocida
    row = 'SELECT  ref_rowid_tc ' \
          'FROM ventas WHERE id = '+str(id[0])+ ' ORDER BY ventas.rowid DESC'  #

    cur[1].execute(row)
    ultima_linea_conocida = cur[1].fetchone()

    if ultima_linea_conocida == None :          # si el registro esta vacio para el id


        #entonces buscar el primer registro de transaccion en crudo
        valores= 'SELECT rowid, fecha_cons, hora_cons, precio, cajas_pedidas, cajas_rest, fecha_env ' \
                 'FROM crudo WHERE id='+str(id[0])+ ' AND cajas_rest <> '+str(id[2])+' ORDER BY ' \
                                                                                    'crudo.rowid ASC'
        # print("valores",valores)
        cur[1].execute(valores)
        datos= cur[1].fetchone()
        if datos:
            print("id:", id)
            print("sin registro previo")
            print("datos:", datos)
            print("cajas pedidas", datos[4])
            print("cajas restantes anterior:",id[2])
            print("cajas restantes", datos[5])
            cantidad_cajas_vendidas= int(datos[5])-int(id[2])
            print("cantidad cajas modif",abs(cantidad_cajas_vendidas))
            tiempo_faltante= diferencia_tiempo_consulta_vencimiento(datos[1],datos[2],datos[6])
            # resp= id, fecha_venta, hora_venta, precio_venta, cantidad_vendida, ref_rowid_tc, tiempo faltante en min

            resp = (str(id[0]), str(datos[1]), str(datos[2]), str(datos[3]), str(abs(cantidad_cajas_vendidas)),
                    str(datos[0]), str(tiempo_faltante))
            print(resp)
            if int(id[2]) > int(datos [5]) : # si cajas rest ant > que cajas rest actual = venta
                print("disminucion")
                cur[1].execute('INSERT INTO ventas (id, fecha_venta, hora_venta, precio_venta, cantidad_vendida,'
                               'ref_rowid_tc, tiempo_faltante) values '+ str(resp)+' ;')
                cur[1].execute('UPDATE resumen SET cantidad_restante = '+str(datos[5])+' WHERE id = ' +str(id[0])+';')
                # cur[0].commit()

            else:
                print("aumento")
                cur[1].execute('INSERT INTO ventas (id, fecha_venta, hora_venta, precio_venta, cantidad_agregada,'
                               'ref_rowid_tc, tiempo_faltante) values ' + str(resp) + ' ;')
                cur[1].execute(
                    'UPDATE resumen SET cantidad_restante = ' + str(datos[5]) + ' WHERE id = ' + str(id[0]) + ';')
                # cur[0].commit()

    else:       # si ya existe algun registro previo para el id buscamos si existe siguiente registro en crudo


        valores = 'SELECT rowid, fecha_cons, hora_cons, precio, cajas_pedidas, cajas_rest, fecha_env ' \
                  'FROM crudo WHERE id=' + str(id[0]) + ' AND cajas_rest <> ' + str(id[2]) + ' AND rowid >' \
                 ''+str(*ultima_linea_conocida)+' ORDER BY crudo.rowid ASC'

        # print("registra nuevos valores:",valores)
        cur[1].execute(valores)
        datos = cur[1].fetchone()
        # print(datos)

        if datos:
            print("id:", id)
            print("con registro previo")
            print("de ultima lin conocida en ventas: ", ultima_linea_conocida)

            print("datos:", datos)
            print("cajas pedidas", datos[4])
            print("cajas restantes anterior:", id[2])
            print("cajas restantes", datos[5])
            cantidad_cajas_vendidas = int(datos[5]) - int(id[2])
            print("cantidad cajas modif", abs(cantidad_cajas_vendidas))
            tiempo_faltante = diferencia_tiempo_consulta_vencimiento(datos[1], datos[2], datos[6])
            # resp= id, fecha_venta, hora_venta, precio_venta, cantidad_vendida, ref_rowid_tc, tiempo faltante en
            # min

            resp = (str(id[0]), str(datos[1]), str(datos[2]), str(datos[3]), str(abs(cantidad_cajas_vendidas)),
                    str(datos[0]), str(tiempo_faltante))
            print("respuesta",resp)
            if int(id[2]) > int(datos[5]):  # si cajas rest ant > que cajas rest actual = venta
                print("disminucion")
                cur[1].execute('INSERT INTO ventas (id, fecha_venta, hora_venta, precio_venta, cantidad_vendida,'
                               'ref_rowid_tc, tiempo_faltante) values ' + str(resp) + ' ;')
                cur[1].execute(
                    'UPDATE resumen SET cantidad_restante = ' + str(datos[5]) + ' WHERE id = ' + str(id[0]) + ';')
                # cur[0].commit()

            else:
                print("aumento")
                cur[1].execute('INSERT INTO ventas (id, fecha_venta, hora_venta, precio_venta, cantidad_agregada,'
                               'ref_rowid_tc, tiempo_faltante) values ' + str(resp) + ' ;')
                cur[1].execute(
                    'UPDATE resumen SET cantidad_restante = ' + str(datos[5]) + ' WHERE id = ' + str(id[0]) + ';')
                # cur[0].commit()
        # buscamos si existe un registro de transaccion mas reciente en crudo
cur[0].commit()

print("---------------FIN PASO 4-------------------")


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#                                paso 5 : actualizar estado activo si aun esta en brecha de tiempo

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
print("---------------INICIO PASO 5-------------------")

ahora_fecha_format = datetime.datetime.now().strftime("%Y-%m-%d")
ahora_hora_format = datetime.datetime.now().strftime("%H:%M")

cur[1].execute('SELECT id, fecha_envio, esta_activo, minutos_restantes FROM resumen')    #para el id en la tabla
# resumen
resultado= cur[1].fetchall()
# print(resultado)

for id in resultado:
    if id[2] == None:
        cur[1].execute('UPDATE resumen SET esta_activo =1 WHERE id= ' + str(id[0]) + ';')
    elif id[2] ==1 :    # si esta activo
        tiempo=diferencia_tiempo_consulta_vencimiento(ahora_fecha_format,ahora_hora_format,id[1])
        # print(tiempo)
        if tiempo <=0 : # si tiempo restante calculado es <= a 0 esta_activo =0
            cur[1].execute('UPDATE resumen SET esta_activo =0 WHERE id= ' + str(id[0]) + ';')
            cur[1].execute('UPDATE resumen SET minutos_restantes =-110 WHERE id= ' + str(id[0]) + ';')
        else :
            cur[1].execute(
                'UPDATE resumen SET minutos_restantes = ' + str(tiempo) + ' WHERE id = ' + str(id[0]) + ';')
cur[0].commit()


print("---------------FIN PASO 5-------------------")
# ////////////////////////////// quitar XXXX-XX-XX--MON de fecha_cons en tabla crudo////////////////////////

# cur[1].execute('SELECT rowid, precio FROM crudo')
# seleccion = cur[1]. fetchall()
# print("seleccion:",seleccion)
# for id in seleccion:
#     print("id:", id[1],"-")
#     if len(id[1]) < 6 :
#         print(id[1])
#         sentencia="UPDATE crudo SET precio ='"+str(id[1][:5])+ "   ' WHERE rowid="+str(id[0])+";"
#         print(sentencia,"------")
#         cur[1].execute(sentencia)
# cur[0].commit()

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////




# # ////////////////////////////// quitar $ de precio inicial en tabla crudo////////////////////////
#
# cur[1].execute('SELECT rowid, precio FROM crudo')
# seleccion = cur[1]. fetchall()
# print(seleccion)
# for id in seleccion:
#     if id[1][0] == '$' :
#         print(id[1])
#
#         sentencia="UPDATE crudo SET precio ="+str(id[1][1:])+" WHERE rowid="+str(id[0])+";"
#         print(sentencia)
#         cur[1].execute(sentencia)
#     cur[0].commit()

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



# resultado =cur[1].fetchall()
#
# print("resultado:", resultado)
# for id in resultado:
#     database.db_ejecutar(cur[1],variables.sql_insertar_id_en_resumen,id)
# cur[0].commit()
#
# for id in resultado:
#     sentencia ='SELECT rowid, nombre, fecha_cons, precio, cajas_pedidas, fecha_env FROM crudo WHERE id='+ str(*id) +' ORDER ' \
#                                                                                                             'BY rowid ASC'
#     # print(sentencia)
#     cur[1].execute(sentencia)
#     resp=cur[1].fetchall()
#     # resp2=cur[1].fetchone()
#     print("fetchall",*resp)
#     # print("fetchone",*id, *resp2)