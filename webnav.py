import time
import datetime
#import geckodriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import variables
import database
import user

# Create a user file that contains :
# usuario="username"
# contra="password"
import traceback

def abrir_explorador(url):
    print("empieza abrir exploradon")
    driver = webdriver.Firefox()

    driver.get(url)
    print("coneccion establecida con firefox")
    time.sleep(10)

    return (driver)


def ingresar(driver, usuario, pwd):
    username = driver.find_element(By.XPATH, '/html/body/table[3]/tbody/tr/td[2]/input[1]')
    username.clear()
    username.send_keys(usuario)
    print("usuario ingresado")
    time.sleep(5)

    password = driver.find_element(By.XPATH, '/html/body/table[3]/tbody/tr/td[2]/input[2]')
    time.sleep(2)
    password.clear()
    password.send_keys(pwd)
    print("password ingresado")

    password.send_keys(Keys.ENTER)
    time.sleep(5)

    if (driver.current_url == "https://www.flowerbuyer.com/purchases/Welcome.asp?G=Y&Login=Y&notice=Y&New_offer=N"):
        print("Ingreso exitoso !")
        return (True)
    else:
        print("Ingreso fallido")
        return (False)


def seleccion_condiciones(driver, variedad, imp_fechas=1, imp_variedades=1):

    driver.switch_to.frame("default_top")   # cambiar foco a frame default top (lugar donde se seleccionan las diversas
    # opciones de filtrado)
    time.sleep(5)

    drp = driver.find_element_by_name('edate')  # busqueda del contenedor de fechas hasta
    todas_fechas = drp.find_elements_by_tag_name("option")  # seleccionar todas las opciones
    cuantas_fechas = len(todas_fechas)  # obtener cuantas fechas disponibles hay

    if (imp_fechas):    # si opcion imprimir fechas disponibles esta habilitada

        print("Total de fechas:", cuantas_fechas)

        for fecha in todas_fechas:
            print("fecha: %s" % fecha.get_attribute("value"))


    select = Select(driver.find_element_by_name('edate'))   # buscar contenedor fecha hasta
    select.select_by_index(cuantas_fechas - 1)  # seleccionar ultima fecha disponible
    print("fecha maxima seleccionada")

    #                           seccion de seleccion de producto

    time.sleep(2)
    drp2 = driver.find_element_by_name('product')   # buscar contenedor de productos

    if (imp_variedades): # si opcion imprimir variedades,

        todos_productos = drp2.find_elements_by_tag_name("option")  # buscar todas las opciones
        cuantos_productos = len(todos_productos)
        print("total de productos: ", cuantos_productos)    # imprimir cantidad productos posibles

        for producto in todos_productos:
            print("producto: ", producto.get_attribute("value"), producto.get_attribute("text")) # imprimir  cada
            # producto

    try:    # intentar seleccionar producto 'product'
        select2 = Select(driver.find_element_by_name('product'))    # buscar seleccionador productos
        select2.select_by_value(str(variedad))                      # selecciona el producto pasado en variedad

        driver.switch_to.default_content()                          # regresa a esquema origen
        time.sleep(5)
        print("producto seleccionado")
        return (True)  # todos ha salido bien

    except: # si no pudo continuar con todos los productos
        print("producto no ha podido ser seleccionado")
        driver.switch_to.default_content()                          # regresa a esquema origen
        return (False)  # algo ha salido mal

def cerrar_sesion (driver):
    try:
        driver.switch_to.default_content()
        driver.switch_to.frame('default_top')
        driver.find_element_by_xpath(
            '/html/body/form/center/table[1]/tbody/tr[1]/td/table/tbody/tr[1]/td/div/ul/li[11]/a').click()
        time.sleep(10)
        return True
    except:
        return False

def averiguar_porte_tabla (driver):
    try:
        driver.switch_to.default_content()
        driver.switch_to.frame('default_Body_right')
        time.sleep(5)

        total_filas = len(driver.find_elements_by_xpath('/html/body/center/table/tbody/tr'))
        total_columnas = len(driver.find_elements_by_xpath('/html/body/center/table/tbody/tr[2]/td'))
        return(total_filas,total_columnas)
    except:
        return False

def extraer_datos (driver,coneccion,cursor):

    porte_tabla=averiguar_porte_tabla(driver)
    ahora_fecha_format = datetime.datetime.now().strftime("%Y-%m-%d")
    ahora_dia_sem_format=datetime.datetime.now().strftime("%a")
    ahora_hora_format = datetime.datetime.now().strftime("%H:%M")
    ahora_sem_num_format = datetime.datetime.now().strftime("%V")

    for f in range(2, porte_tabla[0] - 1):
        lista = []
        lista.append(str(ahora_fecha_format))
        lista.append(str(ahora_dia_sem_format))
        lista.append(str(ahora_hora_format))
        lista.append(str(ahora_sem_num_format))
        for c in range(1, porte_tabla[1]):
            if (c == 1):
                lista.append(driver.find_element_by_xpath(
                    "/html/body/center/table/tbody/tr[" + str(f) + "]/td[" + str(c) + "]/input[1]").get_attribute(
                    'value'))  # ingresar identidad unica
                lista.append(driver.find_element_by_xpath(
                    "/html/body/center/table/tbody/tr[" + str(f) + "]/td[" + str(c) + "]/input[4]").get_attribute(
                    'value'))  # ingresar nombre generico sin opciones seleccionables
            # print(f,c," :",driver.find_element_by_xpath("/html/body/center/table/tbody/tr["+str(f)+"]/td["+str(
            # c)+"]").text)
            elif (c==6):
                a=driver.find_element_by_xpath(
                    "/html/body/center/table/tbody/tr[" + str(f) + "]/td[" + str(c) + "]").text
                lista.append(a[1:])
            else:
                lista.append(driver.find_element_by_xpath(
                    "/html/body/center/table/tbody/tr[" + str(f) + "]/td[" + str(c) + "]").text)
        # print(lista)
        entradas = tuple(lista)
        # print("entradas:", entradas)
        database.db_ejecutar(cursor,variables.sql_insertar_tabla_crudo, entradas)
        coneccion.commit()
        del entradas
        del lista

    cerrar_sesion(driver)
print("datos extraidos")
        # cur.execute('INSERT INTO crudo(hora, id, nombre, fecha_env, unidad, cantidad, caja, precio,
        # cajas_pedidas, '  #             'cajas_rest) '  #             'VALUES(?,?,?,?,?,?,?,?,?,?)', entradas)
        # conn.commit()



def iniciar ():
    driver = abrir_explorador(variables.url)
    if ingresar(driver,user.usuario,user.contra) :
        if seleccion_condiciones(driver,variables.variedad,imp_fechas=0,imp_variedades=0):
            return driver
        else:
            return False
    else:
        return False
