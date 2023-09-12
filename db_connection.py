import pyodbc

server = 'DESKTOP-JF79DLE\MSSQLSERVER01'
database = 'AplicatieLicenta'
username = ''
password = ''
connection_string = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
connection = pyodbc.connect(connection_string)
cursor = connection.cursor()