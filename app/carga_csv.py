import pandas as pd
import os
from conector_db import get_db_engine

FOLDER_PATH = 'datos' 

def load_all_csv_to_sql():
    """
    Carga todos los archivos CSV en la carpeta 'datos/' a tablas en la DB.
    Las tablas se nombran como 'matricula_AÑO'.
    """
    engine = get_db_engine()
    if not engine:
        return False, "Error de conexión a la DB."

    cargados = 0
    
    # Asegúrate de que la ruta exista
    if not os.path.exists(FOLDER_PATH):
        return False, f"La carpeta '{FOLDER_PATH}' no existe."
        
    for filename in os.listdir(FOLDER_PATH):
        if filename.endswith(".csv"):
            file_path = os.path.join(FOLDER_PATH, filename)
            try:
                año = filename.split('_')[-1].replace('.csv', '')
                table_name = f'matricula_{año}'

                df = pd.read_csv(file_path, sep=';')
                df.columns = [col.lower() for col in df.columns]

                # Cargar el DataFrame a SQL Server
                df.to_sql(name=table_name, con=engine, if_exists='replace', index=False, schema='dbo', chunksize=100000)
                cargados += 1

            except Exception as e:
                print(f"ERROR DE CARGA: Falló el archivo {filename}: {e}")
                return False, f"Error al cargar {filename}. Revisa el formato CSV."
                
    return True, f"Carga masiva completada. {cargados} tablas cargadas."

if __name__ == '__main__':
    success, message = load_all_csv_to_sql()
    print(message)