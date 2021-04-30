from pyvirtualdisplay import Display
import database
import webnav
import variables
import geckodriver_autoinstaller

with Display():
    geckodriver_autoinstaller.install()
    cur = database.iniciar(variables.db_file,variables.nombre_tabla_scratch,variables.sql_crear_tabla_crudo)
    if cur :
        print("base de datos iniciada correctamente")
        driver = webnav.iniciar()
        print("driver",driver)
        if driver :
            print("driver iniciado correctamente, exrayendo datos")
            webnav.extraer_datos(driver,cur[0],cur[1])




    driver.close()
    database.db_cerrar (cur[0])







