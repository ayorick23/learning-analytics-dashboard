# <img src="img/streamlit_red.svg" alt="streamlit-log" width=40> Learning Analytics Dashboard

## Configuración

1. **Colocar el archivo de datos:**
   - Pon `Reporte_LMS.xlsx` en la misma carpeta que `app.py`

2. **Instalar dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar localmente:**

   ```bash
   streamlit run app.py
   ```

4. **Publicar en Streamlit Community Cloud:**
   - Sube este repositorio a GitHub (o solo los dos archivos: `app.py` y `requirements.txt`)
   - Ve a https://share.streamlit.io
   - Conecta tu repositorio → selecciona `app.py` → Deploy
   - **Importante:** Sube el Excel actualizado al repo cada semana (o usa `st.file_uploader` si prefieres que el gerente lo suba directamente)

## Actualización semanal

Reemplaza `Reporte_LMS.xlsx` con la nueva versión y haz commit/push al repositorio.
El dashboard se actualizará automáticamente en minutos.

## Estructura esperada del Excel

- **Hoja `Fact_LMS`:** Datos de cursos y colaboradores
- **Hoja `CC`:** Centros de trabajo, distritos y tipo (Operativa/Administrativa)
- **Hoja `Empleados`:** Datos maestros de empleados

[app](https://learning-analytics-dashboard.streamlit.app/)
