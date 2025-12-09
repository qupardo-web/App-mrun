import pandas as pd
from conector_db import get_db_engine

NOMBRE_INSTITUCION = 'IP ESCUELA DE CONTADORES AUDITORES DE SANTIAGO'

def get_repeated_mruns_analysis():
    """
    Ejecuta la consulta SQL para obtener la trayectoria de alumnos 
    de la institución de interés con matrículas en otras instituciones.
    """
    engine = get_db_engine()
    if not engine:
        return None, "Error de conexión a la DB."
        
    query = f"""
    WITH MRunEAC AS (
        -- 1. Identificar todos los MRUNs únicos de la institución de interés en cualquier año
        SELECT DISTINCT mrun
        FROM dbo.vista_matriculas_unificada
        WHERE nomb_inst = '{NOMBRE_INSTITUCION}'
    )
    , TrayectoriaCruzada AS (
        -- 2. Encontrar todos los registros (trayectoria completa) de esos MRUNs
        SELECT v.cat_periodo, v.mrun, v.nomb_inst, v.nomb_carrera
        FROM dbo.vista_matriculas_unificada v
        INNER JOIN MRunEAC eac ON v.mrun = eac.mrun
    )
    -- 3. Filtrar para obtener solo los MRUNs que tienen registros en OTRA institución
    SELECT 
        t.*
    FROM TrayectoriaCruzada t
    WHERE t.mrun IN (
        SELECT mrun 
        FROM TrayectoriaCruzada
        WHERE nomb_inst != '{NOMBRE_INSTITUCION}' -- Filtro clave
        GROUP BY mrun
    )
    ORDER BY mrun, cat_periodo;
    """
    
    try:
        df_resultado = pd.read_sql(query, engine)
        num_mruns = df_resultado['mrun'].nunique()
        return df_resultado, f"Análisis completado. {num_mruns} alumnos con trayectoria externa encontrados."
        
    except Exception as e:
        return None, f"❌ ERROR al ejecutar la consulta de análisis. ¿Se creó la vista? Detalle: {e}"

if __name__ == '__main__':
    df, message = get_repeated_mruns_analysis()
    print(message)
    if df is not None:
        print(df.head())