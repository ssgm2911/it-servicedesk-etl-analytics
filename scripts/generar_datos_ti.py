import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('es_CO') # Genera datos realistas en español
np.random.seed(42)
random.seed(42)

def generar_reporte_ti_sucio(num_registros=1000):
    categorias = ['Hardware', 'Software', 'Redes y Accesos', 'Impresoras', 'Laptops / Equipos', 'SOFTWARE', 'hardware']
    prioridades = ['Alta', 'Media', 'Baja', 'ALTA', 'Critical', None]
    estados = ['Cerrado', 'Resuelto', 'En Proceso', 'Abierto', 'CERRADO']
    tecnicos = ['Carlos Mendoza', 'Ana Torres', 'Luis Gómez', 'Sofia Ramos', ' Sin Asignar ', 'carlos mendoza']
    
    data = []
    fecha_inicio = datetime(2026, 1, 1)
    
    for i in range(1, num_registros + 1):
        ticket_id = f"TCK-{1000 + i}"
        
        # Fecha de apertura homogénea en el rango
        dias_random = random.randint(0, 180)
        fecha_apertura_dt = fecha_inicio + timedelta(days=dias_random, hours=random.randint(8, 17))
        fecha_apertura = fecha_apertura_dt.strftime("%Y-%m-%d %H:%M:%S")
            
        estado = random.choice(estados)
        if estado in ['Cerrado', 'Resuelto', 'CERRADO']:
            # Horas de resolución realistas: entre 1 y 36 horas
            horas_resolucion = random.randint(1, 36)
            fecha_cierre_dt = fecha_apertura_dt + timedelta(hours=horas_resolucion)
            fecha_cierre = fecha_cierre_dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            fecha_cierre = None
            
        categoria = random.choice(categorias)
        prioridad = random.choice(prioridades)
        tecnico = random.choice(tecnicos)
        usuario = fake.name()
        
        # Inyectar espacios blancos y minúsculas desordenadas
        if random.random() < 0.2 and usuario:
            usuario = f"  {usuario.lower()}  "
            
        costo_reparacion = round(random.uniform(20.0, 500.0), 2) if categoria in ['Hardware', 'Laptops / Equipos', 'hardware'] else 0.0
        # Inyectar valores nulos aleatorios en costo
        if random.random() < 0.1:
            costo_reparacion = None

        data.append({
            'Ticket_ID': ticket_id,
            'Fecha_Apertura': fecha_apertura,
            'Fecha_Cierre': fecha_cierre,
            'Categoria': categoria,
            'Prioridad': prioridad,
            'Estado': estado,
            'Tecnico_Asignado': tecnico,
            'Usuario_Solicitante': usuario,
            'Costo_Reparacion_USD': costo_reparacion
        })

    df = pd.DataFrame(data)
    
    # Guardar como CSV "sucio"
    df.to_csv('tickets_ti_raw.csv', index=False, encoding='utf-8-sig')
    print("✅ Archivo 'tickets_ti_raw.csv' generado exitosamente con 1000 registros y datos 'sucios'.")

if __name__ == "__main__":
    generar_reporte_ti_sucio()