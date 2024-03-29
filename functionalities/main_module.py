"""Modulo principal"""

import data_management.validate_data
from data_management.cypher import Security
from functionalities.register import Register
from functionalities.login import Login
from data_management.json_store import JsonStore
from data_management.json_store_signature import SignatureStore
from functionalities.show_info import ShowInfo
from functionalities.money import Money
from data_management.manage_key import Key


# Función que valida los valores de entrada para registro de usuario
def validate_register():

    user = ""
    validated = False
    while not validated:
        user = input("Introduzca un nombre de usuario: ")
        validated = data_management.validate_data.validate_user(user)

    accesskey = ""
    validated = False
    while not validated:
        accesskey = input("Introduca una clave de acceso: ")
        validated = data_management.validate_data.validate_accesskey(accesskey)

    age = ""
    validated = False
    while not validated:
        age = input("Introduzca fecha de nacimiento(dd/mm/yyyy): ")
        validated = data_management.validate_data.validate_age(age)

    phone = ""
    validated = False
    while not validated:
        phone = input("Introduzca un número de teléfono: ")
        validated = data_management.validate_data.validate_phone(phone)

    identification = ""
    validated = False
    while not validated:
        identification = input("Introduca un documento de identificación(dni/nie): ")
        validated = data_management.validate_data.validate_id(identification)

    return user, accesskey, age, phone, identification


# Función que realiza el registro
def register_user():
    data_validated = validate_register()
    data_register = Register(data_validated[0], data_validated[1], data_validated[2], data_validated[3],
                             data_validated[4])
    data_register.cypher_values()
    key = Key(data_validated[1])
    key.generate_save_key()     # Se genera una clave privada para el sistema sólo si se reliza un registro de usuario nuevo
    print("Usuario registrado correctamente.\n")


# Función que realiza el inicio de sesión
def login_user():
    print("Para iniciar sesión introduzca usuario y contraseña.\n")
    access = False
    while not access:
        user = input("Introduzca el usuario: ")
        accesskey = input("Introduzca la contraseña: ")
        login = Login(user, accesskey)
        result = login.validate_values()
        if result:
            print("Inicio de sesión correcto.\n")
            access = True
        else:
            print("Usuario o contraseña incorrecto.\n")


# Programa principal
def my_program():
    print("Hola bienvenido a la aplicación MyVirtualBank.")
    print("Para usar la aplicación debe ser miembro de nuestro banco.\n")
    login = False   # Variable para controlar el login
    while not login:
        member = input("¿Tiene una cuenta creada?(y/n): ").lower()
        if member == "y":       # Iniciar sesión
            login_user()
            login = True
        elif member == "n":     # No hay cuenta creada
            register = input("¿Quiere crear una cuenta?(y/n): ").lower()
            if register == "y":     # Registro
                json = JsonStore()
                json.empty_json_file()  # Cuando se hece registro de nuevo usuario se eliminan los datos del usuario anterior
                signature_json = SignatureStore()
                signature_json.empty_json_file()    # Tambiñen se eliminan las firmas de las operaciones
                print()
                register_user()
                login = True    # Fin de registro, salir del bucle
            elif register == "n":   # No queremos registro. Fin de programa
                print("Fin de programa.")
                exit()
            else:
                print("Valor introducido incorrecto.\n")
        else:
            print("Valor introducido incorrecto.\n")

    # Iniciado de sesión
    print("Bienvenido a MyVirtualBank.")
    print("A continuación, le mostramos las posibles operaciones a realizar: \n")
    exit_program = False    # Variable para controlar cuando salir del programa
    while not exit_program:
        messages_oper()
        oper = input("¿Qué desea realizar?: ").lower()

        # Usuario elige mostrar información de la cuenta
        if oper == "information":
            print("Para acceder a la información personal se necesita verificación de la identidad.")
            verified = False
            while not verified:
                access = input("Introduzca la contraseña ('exit' para volver): ")
                if access != "exit":
                    security = Security(access)
                    if security.validate_accesskey():   # Comprobar contraseña
                        print("Identidad verificada.\n")
                        information = ShowInfo(access)      # Función que muestra los datos
                        information.show_info()
                        verified = True
                    else:
                        print("Contraseña incorrecta.\n")
                else:
                    print()
                    verified = True

        # Usuario elige extraer dinero
        elif oper == "withdraw":
            print("Para realizar una operación de extracción se necesita verificación de la identidad.")
            verified = False
            while not verified:
                access = input("Introduzca la contraseña ('exit' para volver): ")
                if access != "exit":
                    security = Security(access)
                    if security.validate_accesskey():   # Comprobar contraseña
                        print("Identidad verificada.\n")
                        account_money = security.decode_value("iv_saldo", "saldo")
                        if int(account_money.decode()) != 0:    # Comprobar que haya saldo disponible en la cuenta(no sea 0). Recién registrado siempre es 0 por lo que no se puede extraer dinero antes de haber hecho un ingreso.
                            amount = False
                            while not amount:
                                try:
                                    value = int(input("Introduzca la cantidad a extraer: "))
                                    money = Money(value, access)
                                    checked_money = money.check_money_withdraw()  # Verificar que dinero a extraer sea natural mayor que 0, menor que saldo disponible en cuenta y menor que máx por operación(2000).
                                    if checked_money:
                                        print("Realizando operación.\n")
                                        money.withdraw_money()  # Se realiza la extracción de la cantidad
                                        amount = True
                                    else:
                                        amount = False
                                except ValueError:
                                    print("Valor introducido incorrecto. Debe ser un número positivo mayor que 0.\n")
                            verified = True
                        else:
                            print("No tiene saldo disponible en tu cuenta.\n")
                            verified = True
                    else:
                        print("Contraseña incorrecta.\n")
                else:
                    print()
                    verified = True

        # Usuario elige ingresar dinero
        elif oper == "deposit":
            print("Para realizar una operación de ingreso se necesita verificación de la identidad.")
            verified = False
            while not verified:
                access = input("Introduzca la contraseña ('exit' para volver): ")
                if access != "exit":
                    security = Security(access)
                    if security.validate_accesskey():   # Comprobar contraseña
                        print("Identidad verificada.\n")
                        amount = False
                        while not amount:
                            try:
                                value = int(input("Introduzca la cantidad a ingresar: "))
                                money = Money(value, access)
                                checked_money = money.check_money_deposit()     # Verificar que dinero a extraer sea natural mayor que 0 y menor que máx por operación(2000).
                                if checked_money:
                                    print("Realizando operación.\n")
                                    money.deposit_money()       # Realizar la operación de ingreso
                                    amount = True
                                else:
                                    amount = False
                            except ValueError:
                                print("Valor introducido incorrecto. Debe ser un número positivo.\n")
                        verified = True
                    else:
                        print("Contraseña incorrecta.\n")
                else:
                    print()
                    verified = True

        # Salir del programa
        elif oper == "exit":
            exit_program = True

        else:
            print("Operación inválida.\n")
    print("Fin de programa. ¡Hasta la próxima!\n")
    exit()


# Mensajes del programa
# Mostrar información de las funcionalidades
def messages_oper():
    print("-Para mostrar información de la cuenta, introduzca 'information'.\n")
    print("-Para extraer dinero de tu cuenta, introduzca 'withdraw'.\n")
    print("-Para depositar dinero en tu cuenta, introduzca 'deposit'.\n")
    print("-Para salir del programa, introduzca 'exit'.\n")
