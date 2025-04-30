import streamlit as st
import pandas as pd
import random

# Función para validar
def datos_completos(df):
    if df.isnull().values.any() or (df["Demandas"] <= 0).any():
        return False
    return True

# Configuración para pantalla completa
st.set_page_config(layout="wide")

# Lógica para navegar entre páginas
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"  # Página inicial por defecto
    
# Página inicial
if st.session_state.pagina == "inicio":

    st.title("Transformada Inversa")
    st.divider()

    col1, col2 = st.columns([1, 2], gap = "large")
    
    marcador = True

    with col1:
        st.subheader("Ingreso de datos")
        dias = st.number_input("Número de días", min_value = 0, step = 1)
        
        if dias:
            # Generando Números Aleatorios
            if st.button("Generar Número Aleatorios", key = "aleatorio"):
                marcador = False
                aleatorio = [random.randint(1, 10) for _ in range(dias)]
                    
                with col2:
                    df = pd.DataFrame({
                        "Día": [f"{i+1}" for i in range(dias)],
                        "Demandas": aleatorio
                    })
                    
                    # Mostrando el DataFrame (solo visual)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Guardando Datos
                    st.session_state.demandas_aleatorias = df["Demandas"].copy()

                    # Al presionar el botón, se guarda directamente el df que tú creaste (ya con los aleatorios)
                    if st.button("Resolver"):
                        st.session_state.pagina = "Resolver"
                        st.rerun()
    with col2:
        if dias > 0 and marcador == True:
            df = pd.DataFrame({
                "Día": [f"{i+1}" for i in range(dias)],
                "Demandas": [0 for _ in range(dias)]
            })

            # Dataframe editable
            df_editado = st.data_editor(df, use_container_width = True, hide_index = True)

            # Botón para continuar
            boton_habilitado = datos_completos(df_editado)

            if st.button("Resolver", disabled = not boton_habilitado):
                st.session_state.demandas = df_editado["Demandas"].copy() # Copia de la demanda (ya editada)
                st.session_state.pagina = "Resolver"
                st.rerun()
    
    st.session_state.marcador = marcador
                
# Página de resultados
elif st.session_state.pagina == "Resolver":
    
    marcador = st.session_state.get("marcador", True)
    
    st.title("Resultados")
    st.divider()
    
    col1, col2 = st.columns([1, 1], gap = "medium")

    # Llamando a demandas
    if marcador and "demandas" in st.session_state:
        demandas = st.session_state.demandas
    elif not marcador and "demandas_aleatorias" in st.session_state:
        demandas = st.session_state.demandas_aleatorias
    else:
        st.error("No hay datos cargados para resolver. Regresa a la página de inicio.")
        if st.button("Volver al inicio"):
            st.session_state.pagina = "inicio"
            st.rerun()
        st.stop()
    
    with col1:
        st.subheader("Probabilidades Puntuales y Acumuladas")
        lista_demandas = []
        
        # Recorriendo la lista de demandas y agregando a la lista
        for demanda in demandas:
            if demanda not in lista_demandas:
                lista_demandas.append(demanda)
                
        # Contando cuantas veces aparece cada demanda
        conteo = demandas.value_counts().sort_index()
        
        # Conteo total
        contador = 0
        
        conteo_prob = conteo / len(demandas)
        
        lista_demandas.sort()
                
        # Creando el dataframe
        df_probabilidades = pd.DataFrame({
            "X": lista_demandas,
            "p(x)": conteo_prob,
            "P(x)": [conteo_prob[:i+1].sum() for i in range(len(conteo_prob))],
        })
        
        st.dataframe(df_probabilidades, use_container_width = True, hide_index = True)
        
        st.subheader("Criterio de Decisión")
        
        p_acumuladas = df_probabilidades["P(x)"].tolist()

        df_decision = pd.DataFrame({
            "Límite Inferior": [0] + p_acumuladas[:-1],
            "Límite Superior": p_acumuladas,
        })
        
        st.dataframe(df_decision, use_container_width = True, hide_index = True)
        
    with col2:
        st.subheader("Tabla Final")
        
        # Generando ri
        ri = []
        
        # Número de días a simular
        dias_sim = st.number_input("Número de días a simular", min_value = 0, step = 1)
        
        for num in range(dias_sim):
            num = random.random()
            ri.append(num)
            
        df_final = pd.DataFrame({
            "Día": [f"{i+1}" for i in range(dias_sim)],
            "ri": ri,
            "Demanda Diaria": 0
        })    
        
        # Asignando demanda diaria
        demanda_diaria = []

        for r in ri:
            for idx, row in df_decision.iterrows():
                if row["Límite Inferior"] <= r < row["Límite Superior"]:
                    demanda_diaria.append(df_probabilidades.iloc[idx]["X"])
                    break
                
        df_final["Demanda Diaria"] = demanda_diaria
        
        # Agregando la suma total
        df_final.loc[len(df_final)] = ["Total", None, df_final["Demanda Diaria"].sum()]
        
        st.dataframe(df_final, use_container_width = True, hide_index = True)
        
        # Botón para volver al inicio
        if st.button("Volver al inicio"):
            st.session_state.pagina = "inicio"
            st.rerun()