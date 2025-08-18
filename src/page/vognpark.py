import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
from utils.database_connection import get_vognpark_db
from utils.util import get_drivmiddel_icon, get_traek_icon

db_client = get_vognpark_db()


def get_vognpark_overview():
    col_1 = st.columns([1])[0]

    with col_1:
        content_tabs = sac.tabs([
            sac.TabsItem('Vognparkoversigt', tag='Køretøjer i Randers Kommune', icon='bi bi-ev-front'),
        ], color='dark', size='md', position='top', align='start', use_container_width=True)

    try:
        if 'vognpark_data' not in st.session_state:
            results = []
            with st.spinner('Indlæser vognpark data...'):
                query = """
                SELECT "Level_1", "Level_2", "Level_3", "Level_4", "Level_5",
                       "Art", "Træk", "Drivmiddel", "Reg. nr.", "Mærke", "Model"
                FROM vognpark_data
                """
                result = db_client.execute_sql(query)
                columns = [
                    "Level_1", "Level_2", "Level_3", "Level_4", "Level_5",
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

                search_query = st.text_input("Søg køretøj", value="", placeholder="Søg fx Reg.Nr, Mærke", label_visibility="collapsed")

                hierarki_1_options = sorted(data["Level_1"].dropna().unique().tolist())
                hierarki_1_filter = st.selectbox("Hierarki 1", options=["Alle"] + hierarki_1_options)
                hierarki_2_options = sorted(data[data["Level_1"] == hierarki_1_filter]["Level_2"].dropna().unique().tolist()) if hierarki_1_filter != "Alle" else []
                hierarki_2_filter = st.selectbox("Hierarki 2", options=["Alle"] + hierarki_2_options) if hierarki_1_filter != "Alle" else "Alle"
                hierarki_3_options = sorted(data[(data["Level_1"] == hierarki_1_filter) & (data["Level_2"] == hierarki_2_filter)]["Level_3"].dropna().unique().tolist()) if hierarki_2_filter != "Alle" else []
                hierarki_3_filter = st.selectbox("Hierarki 3", options=["Alle"] + hierarki_3_options) if hierarki_2_filter != "Alle" else "Alle"
                hierarki_4_options = sorted(data[(data["Level_1"] == hierarki_1_filter) & (data["Level_2"] == hierarki_2_filter) & (data["Level_3"] == hierarki_3_filter)]["Level_4"].dropna().unique().tolist()) if hierarki_3_filter != "Alle" else []
                hierarki_4_filter = st.selectbox("Hierarki 4", options=["Alle"] + hierarki_4_options) if hierarki_3_filter != "Alle" else "Alle"
                hierarki_5_options = sorted(data[(data["Level_1"] == hierarki_1_filter) & (data["Level_2"] == hierarki_2_filter) & (data["Level_3"] == hierarki_3_filter) & (data["Level_4"] == hierarki_4_filter)]["Level_5"].dropna().unique().tolist()) if hierarki_4_filter != "Alle" else []
                hierarki_5_filter = st.selectbox("Hierarki 5", options=["Alle"] + hierarki_5_options) if hierarki_4_filter != "Alle" else "Alle"

                art_options = sorted(data["Art"].dropna().unique().tolist())
                art_filter = st.selectbox("Art", options=["Alle"] + art_options)
                drivmiddel_options = sorted(data["Drivmiddel"].dropna().unique().tolist())
                drivmiddel_filter = st.selectbox("Drivmiddel", options=["Alle"] + drivmiddel_options)
                traek_options = sorted(data["Træk"].dropna().unique().tolist())
                traek_options_display = ["Alle"] + ["Ja" if x is True else "Nej" if x is False else str(x) for x in traek_options]
                traek_filter = st.selectbox("Træk", options=traek_options_display)

            filtered_data = data.copy()
            if search_query.strip():
                filtered_data = filtered_data[
                    filtered_data["Reg. nr."].str.contains(search_query, case=False, na=False) |
                    filtered_data["Mærke"].str.contains(search_query, case=False, na=False)
                ]
            if hierarki_1_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Level_1"] == hierarki_1_filter]
            if hierarki_2_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Level_2"] == hierarki_2_filter]
            if hierarki_3_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Level_3"] == hierarki_3_filter]
            if hierarki_4_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Level_4"] == hierarki_4_filter]
            if hierarki_5_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Level_5"] == hierarki_5_filter]
            if art_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Art"] == art_filter]
            if drivmiddel_filter != "Alle":
                filtered_data = filtered_data[filtered_data["Drivmiddel"] == drivmiddel_filter]
            if traek_filter != "Alle":
                if traek_filter == "Nej":
                    filtered_data = filtered_data[filtered_data["Træk"] == False]
                elif traek_filter == "Ja":
                    filtered_data = filtered_data[filtered_data["Træk"] == True]
                else:
                    filtered_data = filtered_data[filtered_data["Træk"] == traek_filter]

            st.markdown(
                f"<span style='background:#e0e0e0; border-radius:8px; padding:4px 12px; font-size:1rem; margin-left:8px;'>:car: :blue[{len(filtered_data)}] køretøjer fundet</span>",
                unsafe_allow_html=True
            )

            if filtered_data.empty:
                st.warning("Ingen køretøjer matcher dine filtre.")
                st.stop()

            for i, row in filtered_data.iterrows():
                regnr = row['Reg. nr.'] or 'Ikke angivet'
                maerke = row['Mærke'] if pd.notna(row['Mærke']) and row['Mærke'] != "" else None
                model = row['Model'] if pd.notna(row['Model']) and row['Model'] != "" else None

                title = f"**{regnr}**\n{maerke or ''} {model or ''}".strip()

                with st.expander(title):
                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(90deg, #f8f4ed 80%, #e0e0e0 100%);
                            padding: 1.2rem;
                            border-radius: 12px;
                            margin-bottom: 1rem;
                            border: 1px solid #9E9E9E;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                            display: flex;
                            flex-direction: row;
                            align-items: center;
                            gap: 2rem;
                        ">
                            <div style="flex:1;">
                                <p style="margin:0.2rem 0;"><strong>Reg. nr.:</strong> {regnr}</p>
                                <p style="margin:0.2rem 0;"><strong>Mærke:</strong> {maerke or 'Ikke angivet'}</p>
                                <p style="margin:0.2rem 0;"><strong>Model:</strong> {model or 'Ikke angivet'}</p>
                                <p style="margin:0.2rem 0;"><strong>Art:</strong> {row['Art'] or 'Ikke angivet'}</p>
                            </div>
                            <div style="flex:0.5; text-align:center;">
                                <p style="margin:0.2rem 0;"><strong>Drivmiddel:</strong> {get_drivmiddel_icon(row['Drivmiddel'])}</p>
                                <p style="margin:0.2rem 0;"><strong>Træk:</strong> {get_traek_icon(row['Træk'])}</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    except Exception as e:
        st.error(f'An error occurred:: {e}')
    finally:
        db_client.close_connection()
