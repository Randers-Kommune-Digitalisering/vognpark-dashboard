import streamlit as st
import streamlit_antd_components as sac
import pandas as pd
import io
from utils.database_connection import get_vognpark_db
from utils.util import get_drivmiddel_icon, get_traek_icon, get_most_specific_level, level_1_display_map

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
                SELECT "Level_1", "Level_2", "Level_3", "Level_4", "Level_5", "Level_6",
                       "Art", "Træk", "Drivmiddel", "Reg. nr.", "Mærke", "Model",
                       "Anvendelse", "Stel nr. "
                FROM vognpark_data
                """
                result = db_client.execute_sql(query)
                columns = [
                    "Level_1", "Level_2", "Level_3", "Level_4", "Level_5", "Level_6",
                    "Art", "Træk", "Drivmiddel", "Reg. nr.", "Mærke", "Model",
                    "Anvendelse", "Stel nr. "
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

                hierarki_1_options_raw = sorted(data["Level_1"].dropna().unique().tolist())
                hierarki_1_options = [level_1_display_map.get(x, x) for x in hierarki_1_options_raw]

                if "Ukendt tilhørsforhold" in hierarki_1_options:
                    hierarki_1_options = [opt for opt in hierarki_1_options if opt != "Ukendt tilhørsforhold"] + ["Ukendt tilhørsforhold"]

                hierarki_1_filter = st.selectbox("Forvaltning", options=["Alle"] + hierarki_1_options)

                display_to_raw = {v: k for k, v in level_1_display_map.items()}
                selected_level_1_raw = display_to_raw.get(hierarki_1_filter, hierarki_1_filter)

                enhed_data = data if hierarki_1_filter == "Alle" else data[data["Level_1"] == selected_level_1_raw]

                enhed_options = []
                for _, row in enhed_data.iterrows():
                    if pd.notna(row["Level_4"]) and row["Level_4"] != "":
                        enhed_options.append(row["Level_4"])
                    elif pd.notna(row["Level_3"]) and row["Level_3"] != "":
                        enhed_options.append(row["Level_3"])
                    elif pd.notna(row["Level_2"]) and row["Level_2"] != "":
                        enhed_options.append(row["Level_2"])
                enhed_options = sorted(set(enhed_options))

                enhed_filter = st.selectbox("Enhed", options=["Alle"] + enhed_options)

                art_options_raw = sorted(data["Art"].dropna().unique().tolist())
                art_options = []
                for art in art_options_raw:
                    if art in ["Personbil", "Stor personbil", "Varebil"]:
                        continue
                    art_options.append(art)
                art_options = ["Personbil/Varebil"] + art_options
                art_filter = st.multiselect("Art", options=art_options, default=[], placeholder="Vælg art")

                drivmiddel_options = sorted(data["Drivmiddel"].dropna().unique().tolist())
                drivmiddel_filter = st.multiselect("Drivmiddel", options=drivmiddel_options, default=[], placeholder="Vælg drivmiddel")

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
                filtered_data = filtered_data[filtered_data["Level_1"] == selected_level_1_raw]
            if enhed_filter != "Alle":
                filtered_data = filtered_data[
                    ((filtered_data["Level_4"] == enhed_filter) & filtered_data["Level_4"].notna() & (filtered_data["Level_4"] != "")) |
                    ((filtered_data["Level_4"].isna() | (filtered_data["Level_4"] == "")) &
                     (filtered_data["Level_3"] == enhed_filter) & filtered_data["Level_3"].notna() & (filtered_data["Level_3"] != "")) |
                    ((filtered_data["Level_4"].isna() | (filtered_data["Level_4"] == "")) &
                     (filtered_data["Level_3"].isna() | (filtered_data["Level_3"] == "")) &
                     (filtered_data["Level_2"] == enhed_filter) & filtered_data["Level_2"].notna() & (filtered_data["Level_2"] != ""))
                ]
            if art_filter:
                art_types = []
                for af in art_filter:
                    if af == "Personbil/Varebil":
                        art_types.extend(["Personbil", "Stor personbil", "Varebil"])
                    else:
                        art_types.append(af)
                filtered_data = filtered_data[filtered_data["Art"].isin(art_types)]
            if drivmiddel_filter:
                filtered_data = filtered_data[filtered_data["Drivmiddel"].isin(drivmiddel_filter)]
            if traek_filter != "Alle":
                filtered_data = filtered_data[
                    filtered_data["Træk"].apply(lambda x: "Ja" if x is True else "Nej" if x is False else str(x)) == traek_filter
                ]

            st.markdown(
                f"<span style='background:#e0e0e0; border-radius:8px; padding:4px 12px; font-size:1rem; margin-left:8px;'>🚗 :blue[{len(filtered_data)}] køretøjer fundet</span>",
                unsafe_allow_html=True
            )

            if filtered_data.empty:
                st.warning("Ingen køretøjer matcher dine filtre.")
                st.stop()

            filter_navn = ""
            if hierarki_1_filter != "Alle":
                filter_navn += f"_{hierarki_1_filter.lower().replace(' ', '_')}"
            if enhed_filter != "Alle":
                filter_navn += f"_{enhed_filter.lower().replace(' ', '_')}"

            filnavn = f"vognpark{filter_navn}_eksport.xlsx"

            export_df = filtered_data.copy()
            export_df = export_df[[
                "Level_1", "Level_2", "Level_3", "Level_4", "Level_5", "Level_6",
                "Art", "Træk", "Drivmiddel", "Reg. nr.", "Mærke", "Model",
                "Anvendelse", "Stel nr. "
            ]]
            export_df = export_df.rename(columns={"Level_1": "Forvaltning"})
            export_df["Forvaltning"] = export_df["Forvaltning"].map(lambda x: level_1_display_map.get(x, x))
            export_df["Træk"] = export_df["Træk"].map(lambda x: "Ja" if x is True else "Nej" if x is False else x)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Vognpark')
                worksheet = writer.sheets['Vognpark']
                for i, col in enumerate(export_df.columns):
                    max_len = max(
                        export_df[col].astype(str).map(len).max(),
                        len(col)
                    ) + 2
                    worksheet.set_column(i, i, max_len)
            output.seek(0)
            st.download_button(
                label="Eksporter viste køretøjer til Excel",
                data=output,
                file_name=filnavn,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                help="Download de filtrerede køretøjer som Excel-fil"
            )

            for i, row in filtered_data.iterrows():
                regnr = row['Reg. nr.'] or 'Ikke angivet'
                maerke = row['Mærke'] if pd.notna(row['Mærke']) and row['Mærke'] != "" else None
                model = row['Model'] if pd.notna(row['Model']) and row['Model'] != "" else None
                most_specific_level = get_most_specific_level(row)

                regnr = regnr.strip()
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
                                <p style="margin:0.2rem 0;"><strong>Mærke:</strong> {maerke or 'Ikke oplyst'}</p>
                                <p style="margin:0.2rem 0;"><strong>Forvaltning:</strong> {level_1_display_map.get(row['Level_1'], row['Level_1'])}</p>
                                <p style="margin:0.2rem 0;"><strong>Enhed:</strong> {most_specific_level}</p>
                            </div>
                            <div style="flex:0.5; text-align:center;">
                                <p style="margin:0.2rem 0;"><strong>Model:</strong> {model or 'Ikke oplyst'}</p>
                                <p style="margin:0.2rem 0;"><strong>Art:</strong> {row['Art'] or 'Ikke oplyst'}</p>
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
