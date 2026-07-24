import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import sys

# ---------------------------------------------------------
# 1. CONFIGURACIÓN DE CONEXIÓN A MYSQL
# ---------------------------------------------------------
DB_USER = 'root'
DB_PASS = 'Silvio291197'  # <--- Coloca tu contraseña de MySQL aquí
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'ti_service_desk'

# Cadena de conexión usando SQLAlchemy y PyMySQL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def ejecutar_pipeline_etl():
    print("🚀 Iniciando Pipeline ETL de Servicio de TI...")

    # ---------------------------------------------------------
    # 2. EXTRAER (Extract)
    # ---------------------------------------------------------
    try:
        df_raw = pd.read_csv('tickets_ti_raw.csv')
        print(f"📥 [EXTRACT] Archivo 'tickets_ti_raw.csv' cargado exitosamente con {len(df_raw)} registros.")
    except Exception as e:
        print(f"❌ Error al cargar el archivo CSV: {e}")
        sys.exit()

    df = df_raw.copy()

    # ---------------------------------------------------------
    # 3. TRANSFORMAR (Transform)
    # ---------------------------------------------------------
    print("🧹 [TRANSFORM] Aplicando limpieza y reglas de negocio...")

    # A. Limpieza de Cadenas / Texto
    cols_texto = ['Categoria', 'Prioridad', 'Estado', 'Tecnico_Asignado', 'Usuario_Solicitante']
    for col in cols_texto:
        df[col] = df[col].astype(str).str.strip().str.title()
        # Reemplazar valores nulos representados como texto 'None' o 'Nan'
        df[col] = df[col].replace({'None': 'No Especificado', 'Nan': 'No Especificado'})

    # B. Homogeneizar Categorías Específicas
    mapeo_categorias = {
        'Hardware': 'Hardware',
        'Laptops / Equipos': 'Hardware',
        'Software': 'Software',
        'Redes Y Accesos': 'Redes & Accesos',
        'Impresoras': 'Periféricos'
    }
    df['Categoria'] = df['Categoria'].map(mapeo_categorias).fillna('Otros')

    # C. Homogeneizar Prioridades
    df['Prioridad'] = df['Prioridad'].replace({'Critical': 'Alta', 'No Especificado': 'Media'})

    # D. Estandarizar Fechas (Parsing flexible para manejar formatos mixtos)
    df['Fecha_Apertura'] = pd.to_datetime(df['Fecha_Apertura'], format='mixed', errors='coerce')
    df['Fecha_Cierre'] = pd.to_datetime(df['Fecha_Cierre'], format='mixed', errors='coerce')


    # E. Cálculo del Tiempo de Resolución en Horas con Validación de Calidad (Data Quality Check)
    df['Tiempo_Resolucion_Horas'] = (df['Fecha_Cierre'] - df['Fecha_Apertura']).dt.total_seconds() / 3600.0
    # REGLA DE CALIDAD: Si el tiempo es negativo (fecha de cierre anterior a apertura), corregir o filtrar a NaN
    df.loc[df['Tiempo_Resolucion_Horas'] < 0, 'Tiempo_Resolucion_Horas'] = np.nan
    df['Tiempo_Resolucion_Horas'] = df['Tiempo_Resolucion_Horas'].round(2)

    # F. Evaluación de Cumplimiento de SLA (Regla de negocio de TI)
    # Target SLA: Alta <= 12 hrs, Media <= 24 hrs, Baja <= 48 hrs
    def evaluar_sla(row):
        if pd.isna(row['Tiempo_Resolucion_Horas']):
            return 'Pendiente'
        
        prioridad = row['Prioridad']
        horas = row['Tiempo_Resolucion_Horas']
        
        if prioridad == 'Alta' and horas <= 12:
            return 'Cumplido'
        elif prioridad == 'Media' and horas <= 24:
            return 'Cumplido'
        elif prioridad == 'Baja' and horas <= 48:
            return 'Cumplido'
        else:
            return 'Incumplido'

    df['Estado_SLA'] = df.apply(evaluar_sla, axis=1)

    # G. Imputación de Valores Nulos en Costos
    df['Costo_Reparacion_USD'] = df['Costo_Reparacion_USD'].fillna(0.0)

    print("✅ [TRANSFORM] Limpieza y creación de variables completadas.")

    # ---------------------------------------------------------
    # 4. CARGAR (Load)
    # ---------------------------------------------------------
    print("🛢️ [LOAD] Conectando a MySQL y guardando datos procesados...")
    try:
        engine = create_engine(DATABASE_URL)
        
        # Cargar el DataFrame a la tabla 'tickets_procesados' en MySQL
        df.to_sql(
            name='tickets_procesados',
            con=engine,
            if_exists='replace', # Reemplaza la tabla si ya existe para ejecución idempotente
            index=False
        )
        print("🎉 [LOAD] ¡Datos insertados exitosamente en la tabla 'tickets_procesados' de MySQL!")
    except Exception as e:
        print(f"❌ Error al conectar o cargar datos a MySQL: {e}")

if __name__ == "__main__":
    ejecutar_pipeline_etl()