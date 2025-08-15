import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
from utils.database_connection import get_vognpark_db

db_client = get_vognpark_db()


def get_vognpark_overview():
    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Vognparkoversigt', tag='Køretøjer i Randers Kommune', icon='bi bi-truck'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

    try:
        if 'vognpark_data' not in st.session_state:
            results = []
            with st.spinner('Indlæser vognpark data...'):
                query = """
                SELECT "Level_1", "Level_2", "Level_3", "Level_4", "Level_5", "Level_6",
                       "Art", "Træk", "Drivmiddel", "Reg. nr.", "Mærke", "Model"
                FROM vognpark_data
                """
                result = db_client.execute_sql(query)
                columns = [
                    "Level_1", "Level_2", "Level_3", "Level_4", "Level_5", "Level_6",
                    "Art", "Træk", "Drivmiddel", "Reg. nr.", "Mærke", "Model"
                ]
                if result is not None:
                    results.append(pd.DataFrame(result, columns=columns))
                else:
                    st.error("Kunne ikke hente data fra vognpark databasen.")
                    return

            if results:
                st.session_state.vognpark_data = pd.concat(results, ignore_index=True)
            else:
                st.error("Ingen data at vise.")
                return

        data = st.session_state.vognpark_data

        if content_tabs == 'Vognparkoversigt':
            with st.sidebar:
                st.markdown("### 🔎 Filtrer køretøjer")

                search_query = st.text_input("Søg køretøj", value="", placeholder="Søg fx reg.nr., mærke, model", label_visibility="collapsed")

                level_1_options = sorted(data["Level_1"].dropna().unique().tolist())
                level_1_filter = st.selectbox("Level 1", options=["Alle"] + level_1_options)
                level_2_options = sorted(data[data["Level_1"] == level_1_filter]["Level_2"].dropna().unique().tolist()) if level_1_filter != "Alle" else []
                level_2_filter = st.selectbox("Level 2", options=["Alle"] + level_2_options) if level_1_filter != "Alle" else "Alle"
                level_3_options = sorted(data[(data["Level_1"] == level_1_filter) & (data["Level_2"] == level_2_filter)]["Level_3"].dropna().unique().tolist()) if level_2_filter != "Alle" else []
                level_3_filter = st.selectbox("Level 3", options=["Alle"] + level_3_options) if level_2_filter != "Alle" else "Alle"
                level_4_options = sorted(data[(data["Level_1"] == level_1_filter) & (data["Level_2"] == level_2_filter) & (data["Level_3"] == level_3_filter)]["Level_4"].dropna().unique().tolist()) if level_3_filter != "Alle" else []
                level_4_filter = st.selectbox("Level 4", options=["Alle"] + level_4_options) if level_3_filter != "Alle" else "Alle"
                level_5_options = sorted(data[(data["Level_1"] == level_1_filter) & (data["Level_2"] == level_2_filter) & (data["Level_3"] == level_3_filter) & (data["Level_4"] == level_4_filter)]["Level_5"].dropna().unique().tolist()) if level_4_filter != "Alle" else []
                level_5_filter = st.selectbox("Level 5", options=["Alle"] + level_5_options) if level_4_filter != "Alle" else "Alle"

                art_options = sorted(data["Art"].dropna().unique().tolist())
                art_filter = st.selectbox("Art", options=["Alle"] + art_options)
                drivmiddel_options = sorted(data["Drivmiddel"].dropna().unique().tolist())
                drivmiddel_filter = st.selectbox("Drivmiddel", options=["Alle"] + drivmiddel_options)
                traek_options = sorted(data["Træk"].dropna().unique().tolist())
                traek_filter = st.selectbox("Træk", options=["Alle"] + traek_options)

            filtered_data = data.copy()
            if search_query.strip():
                filtered_data = filtered_data[
                    filtered_data["Reg. nr."].str.contains(search_query, case=False, na=False)
                    | filtered_data["Mærke"].str.contains(search_query, case=False, na=False)
                    | filtered_data["Model"].str.contains(search_query, case=False, na=False)
                ]
            if level_1_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Level_1"] == level_1_filter]
            if level_2_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Level_2"] == level_2_filter]
            if level_3_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Level_3"] == level_3_filter]
            if level_4_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Level_4"] == level_4_filter]
            if level_5_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Level_5"] == level_5_filter]
            if art_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Art"] == art_filter]
            if drivmiddel_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Drivmiddel"] == drivmiddel_filter]
            if traek_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Træk"] == traek_filter]

            st.markdown(
                f"<span style='background:#e0e0e0; border-radius:8px; padding:4px 12px; font-size:0.95rem; margin-left:8px;'>🔎 {len(filtered_data)} køretøjer fundet</span>",
                unsafe_allow_html=True
            )

            if filtered_data.empty:
                st.warning("Ingen køretøjer matcher dine filtre.")
                st.stop()

            for i, row in filtered_data.iterrows():
                with st.expander(f"**{row['Reg. nr.']} - {row['Mærke']} {row['Model']}**"):
                    st.markdown(
                        f"""
                        <div style="background-color:#f8f4ed; padding:1rem; border-radius:10px; margin-bottom:1rem; border: 1px solid #9E9E9E; border-left: 5px solid #9E9E9E;">
                            <p><strong>Reg. nr.:</strong> {row['Reg. nr.'] or 'Ikke angivet'}</p>
                            <p><strong>Mærke:</strong> {row['Mærke'] or 'Ikke angivet'}</p>
                            <p><strong>Model:</strong> {row['Model'] or 'Ikke angivet'}</p>
                            <p><strong>Art:</strong> {row['Art'] or 'Ikke angivet'}</p>
                            <p><strong>Drivmiddel:</strong> {row['Drivmiddel']}</p>
                            <p><strong>Træk:</strong> {row['Træk']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    except Exception as e:
        st.error(f'An error occurred:: {e}')
    finally:
        db_client.close_connection()
