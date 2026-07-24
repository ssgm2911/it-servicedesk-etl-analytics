CREATE DATABASE IF NOT EXISTS ti_service_desk;

## Consulta para saber para comprobar que los valores NULL corresponden únicamente a tickets no cerrados
SELECT 
    Estado, 
    COUNT(*) AS Total_Tickets,
    SUM(CASE WHEN Fecha_Cierre IS NULL THEN 1 ELSE 0 END) AS Con_Fecha_Cierre_Null,
    SUM(CASE WHEN Tiempo_Resolucion_Horas IS NULL THEN 1 ELSE 0 END) AS Con_Tiempo_Null
FROM ti_service_desk.tickets_procesados
GROUP BY Estado;