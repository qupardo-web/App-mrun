from conector_db import get_db_engine
from sqlalchemy import text

def get_table_names(engine):
    """Obtiene los nombres de las tablas de matrícula cargadas (ej: matricula_2022)."""
    # Consulta específica para SQL Server
    query = """
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME LIKE 'matricula_[0-9]%'
    ORDER BY TABLE_NAME;
    """
    try:
        with engine.connect() as connection:

            result = connection.execute(text(query)).fetchall()

            return [row[0] for row in result]

    except Exception as e:
        print(f"ERROR al obtener nombres de tablas: {e}")
        return []

def create_unified_view():
    """Crea o reemplaza la vista unificada 'vista_matriculas_unificada'."""
    engine = get_db_engine()
    if not engine:
        return False, "Error de conexión a la DB."
        
    table_names = get_table_names(engine)
    if not table_names:
        return False, "No se encontraron tablas 'matricula_AÑO' en la DB. ¡Asegúrate de ejecutar carga_csv.py primero!"

    # 1. Definir las consultas
    
    # Consulta para ELIMINAR la vista si existe (debe ir en su propio lote)
    drop_query = """
    IF OBJECT_ID('dbo.vista_matriculas_unificada', 'V') IS NOT NULL
        DROP VIEW dbo.vista_matriculas_unificada;
    """
    
    # Construcción de la parte UNION ALL (se mantiene igual)
    select_statements = []
    for table in table_names:
        select_statements.append(f"""
        SELECT 
            CAST(cat_periodo AS INT) AS cat_periodo, 
            mrun, 
            nomb_inst, 
            nomb_carrera
        FROM dbo.{table}
        """)

    union_query = "\nUNION ALL\n".join(select_statements)

    # Consulta para CREAR la vista (debe ir en su propio lote)
    create_view_query = f"""
    CREATE VIEW dbo.vista_matriculas_unificada AS
    {union_query};
    """

    # 2. Ejecutar las consultas en lotes separados
    try:
        with engine.connect() as connection:
            # LOTE 1: Eliminar la vista (el DROP)
            connection.execute(text(drop_query)) 
            connection.commit()
            
            # LOTE 2: Crear la vista (el CREATE)
            connection.execute(text(create_view_query))
            connection.commit() # Asegura que la creación de la vista se guarde
            
            return True, f"✅ Vista 'vista_matriculas_unificada' creada/actualizada con {len(table_names)} tablas."
            
    except Exception as e:
        return False, f"❌ ERROR al crear la vista SQL: {e}"

if __name__ == '__main__':
    success, message = create_unified_view()
    print(message)