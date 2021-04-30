import database
import matplotlib.pyplot as plt
cur=database.db_obtener_cursor('flower_Buy.db')
#
cur[1].execute('SELECT fecha_envio, precio_inicial, precio_final FROM resumen '
               'WHERE minutos_restantes > 200 '
               'AND esta_activo ==1 '
               'AND fecha_envio like "Apr%"'
               'AND nombre like "% Ext%"'
               'ORDER BY fecha_envio ASC; ')
resultados=cur[1].fetchall()

x=[]
y1=[]
y2=[]
for id in resultados:
    x.append((id[0]))
    y1.append(id[1])
    y2.append(id[2])
print(len(x),x)
print(len(y1),y1)
print(len(y2),y2)

plt.subplot(4,2,1)
plt.bar(x,y1)
plt.legend(['precio inicial'])
plt.subplot(4,2,3)
plt.scatter(x,y2)
# plt.legend(['precio final'])
plt.show()
