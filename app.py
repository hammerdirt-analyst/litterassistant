import streamlit as st
import pandas as pd


import folium
from folium.map import Popup as FoliumPopup
from streamlit_folium import st_folium

import correlation_text
import data_text
import landuse_text
import abstract_intro_text
import session_config
from session_config import data_directory, survey_data, unpack_with_pandas
import geospatial
import reports
import display
from display import display_scatter_plot


# content for report sections
title_section = abstract_intro_text.title_section
data_tab_content = data_text.data_tab_content
land_use_tab_content = landuse_text.land_use_tab_content
land_use_correlation = correlation_text.land_use_correlation

# call data
data = unpack_with_pandas((".", data_directory, survey_data))

# labels and titles
# profile of survey locations

the_most_common_label = {
    'en': 'The most common objects',
    'fr': 'Les objets les plus courants',
    'de': 'Die häufigsten Objekte'
}


def the_most_common_title(an_int: int = 0, session_language: str = 'en'):
    the_title = f'__{the_most_common_label[session_language]} :__ _{an_int}'
    ending = {
        'en': '% of all objects identified_',
        'fr': '% de tous les objets identifiés_',
        'de': '% aller identifizierten Objekte_'
    }
    return f'{the_title} {ending[session_language]}'


profile_of_survey_locations = {
    'en': '__Profile of survey locations__',
    'fr': '__Profil des lieux d\'enquête__',
    'de': '__Profil der Umfragestandorte__'
}

date_selection = {
    'en': 'Select a date range',
    'fr': "Selectionnez une fourchette de dates",
    'de': "Wählen Sie einen Datumsbereich aus"
}

theme_selection = {
    'en': 'Select a theme',
    'fr': 'Selectionnez un theme',
    'de': 'Wählen Sie ein Thema'

}

feature_selection = {
    'en': 'Select a feature',
    'fr': 'Selectionnez une fonctionnalité',
    'de': 'Wählen Sie ein Feature'

}

date_widget_labels = {
    'en': 'Select a start and end date',
    'fr': 'Selectionnez une date de début et de fin',
    'de': 'Wählen Sie ein Start- und Enddatum'
}

tab_labels = ["__Data-Presentation__", "__Land-Use__", "__Forecasting__"]

tab_labels_translations = {
    'en': tab_labels,
    'fr': ["__Présentation des données__", "__Utilisation des terres__", "__Prévisions__"],
    'de': ["__Datenpräsentation__", "__Landnutzung__", "__Prognosen__"]
}

submitt_labels = {
    'en': 'Make a report',
    'fr': 'Faire un rapport',
    'de': 'Bericht erstellen'
}

def main():

    """Reporting litter density"""

    st.title("Litter Density Report")
    st.markdown("__Rapport de densité des déchets / Einheit Abfallobjekte__")
    st.markdown("_Needs translating and revising / Il faut traduire et réviser / Muss übersetzt und überarbeitet "
                "werden_")

    
    with st.sidebar:
        # build report parameters
        st.sidebar.title("Settings / paramètres / Einstellungen")
        st.subheader("Configure / Configurer / Konfigurieren")
        language_choice = st.selectbox("Select a language", session_config.languages, index=1,
                                       key="language_choice")
        
        # collect the column labels and search terms from input
        report_parameters = {}
        theme = st.selectbox(theme_selection[language_choice], session_config.report_themes, index=0, key="select_theme")
        report_parameters.update({"theme": theme})
        feature = session_config.theme_selection_to_column_values[theme]
        # if the feature is for Canton, City or River basin the column is feature_name:
        if theme in ['Canton', 'Municipality', 'River basin']:
            options = data[feature].unique()
            select_a_feature = st.selectbox(feature_selection[language_choice], options, index=0, key="select_target_feature")
        # if the selection is for a river, lake or park the column is feature_type
        if theme in ['River', 'Lake', 'Park']:
            options = data[data.feature_type == feature].feature_name.unique()
            select_a_feature = st.selectbox(feature_selection[language_choice], options, index=None,
                                            key="select_target_feature")

        start, end = session_config.available_dates()
        start, end = pd.to_datetime(start), pd.to_datetime(end)
        report_date_range = st.date_input(date_widget_labels[language_choice],
                                              value=[start, end],
                                              min_value=start,
                                              max_value=end,
                                              key="report_date_range")
            
        submitted = st.button(submitt_labels[language_choice], type="primary", key="verify_parameters")
        
        # if the user has submitted the request
        if submitted:
            
            # update the rest of the parameters and write the report
            # 1. slice the data with the parameters
            # 2. create a report object
            # 3. create the report sections
            # 4. create the land use report
            # 5. create the map markers
            
            report_parameters.update({"feature": select_a_feature})
            report_parameters.update({"start_date": report_date_range[0], "end_date": report_date_range[1]})

            # 1 format date column
            data['date'] = pd.to_datetime(data['date'])

            # apply the requested parameters to the data
            report_data = session_config.apply_requested_parameters(data.copy(), report_parameters)

            # 2 create a report object with the data
            this_report = reports.AReport(dfc=report_data.copy())
            
            # 3 create the report sections
            a_data_summary = this_report.sampling_results_summary()
            admin_boundaries = this_report.administrative_boundaries()
            feature_inventory = this_report.feature_inventory()
            inventory = this_report.object_summary()
            # notation for the most common objects
            the_most_common, pct_total = display.most_common(inventory, language_choice)
            pct_total = pct_total*100
            # scatterplot data
            samp_results = this_report.sample_results(**{'info_columns': ['canton', 'city']})
            samp_results['date'] = pd.to_datetime(samp_results['date'])
            scatter_chart = display_scatter_plot(samp_results['date'], samp_results['pcs/m'],
                                                 data=samp_results, categorical=False,
                                                 session_language=language_choice,
                                                 gradient=True)
            
            # 4 create the components for the land use report
            target_df = this_report.sample_results()
            feature_df = this_report.sampling_conditions()
            
            # 5 create the land use report
            lur_report = geospatial.LandUseReport(target_df, feature_df)
            correlation_matrix = lur_report.correlation_matrix()
            cor_p = lur_report.correlated_pairs()
            lur_report.combine_features(cor_p)

            profiled = geospatial.the_land_use_profile(lur_report.n_samples_per_feature(),
                                                       session_language=language_choice)

            rated = geospatial.the_litter_rate_per_land_use(lur_report.rate_per_feature(),
                                                            session_language=language_choice)
            # create the map markers
            sres = target_df.copy()
            marker_stats, map_bounds = display.map_markers(sres)
            folium_map_kwargs = session_config.folium_map_kwargs

            location_lat = round((map_bounds['max_lat'] + map_bounds['min_lat']) / 2, 2)
            location_lon = round((map_bounds['max_lon'] + map_bounds['min_lon']) / 2, 2)

            folium_map_kwargs.update({'location': [location_lat, location_lon]})
            for label in ['max_lat', 'max_lon']:
                folium_map_kwargs.update({label: map_bounds[label] + .5})
            for label in ['min_lat', 'min_lon']:
                folium_map_kwargs.update({label: map_bounds[label] - .5})

    # The different sections of the report
    data_presentation_tab, land_use_tab, predictions_tab = st.tabs(tab_labels_translations[language_choice])
    
    with data_presentation_tab:
        with st.container():
            st.markdown(title_section[language_choice][0])
            st.markdown(title_section[language_choice][1])
            st.markdown(title_section[language_choice][2])
        
        data_tab_context = data_tab_content[language_choice]
        
        if submitted:
       
            admin_boundaries_list = display.display_boundaries(admin_boundaries, language_choice)
            feature_inventory_list = display.feature_inventory(feature_inventory, language_choice)
            header, content, quants_header, quants = display.display_sampling_result_summary(a_data_summary,
                                                                                             language_choice)

            
            st.bokeh_chart(scatter_chart, use_container_width=True)
            col1, col2 = st.columns([.5, .5], gap='small')
            with col1:
                st.markdown('<br />', unsafe_allow_html=True)
                st.markdown(header)
                st.markdown(content)
            with col2:
                st.markdown('<br />', unsafe_allow_html=True)
                st.markdown(quants_header)
                st.markdown(quants)
            
            st.markdown('<br />', unsafe_allow_html=True)
                
            col3, col4 = st.columns([.5, .5], gap='small')
            
            with st.container():
                with col3:
                    
                    st.markdown(admin_boundaries_list)
                    
                with col4:
                    
                    st.markdown(feature_inventory_list)
            st.markdown('<br />', unsafe_allow_html=True)
            st.markdown(data_tab_context[1])
            
            with st.container():
                # the most common objects
                st.markdown(the_most_common_title(int(pct_total), language_choice))
                
                st.write(the_most_common.to_html(escape=False), unsafe_allow_html=True)
                st.markdown('<br />', unsafe_allow_html=True)
                st.markdown(data_tab_context[2])
                st.markdown(data_tab_context[3])
            
    with land_use_tab:
        land_use_tab_context = land_use_tab_content[language_choice]
        
        st.markdown(land_use_tab_context[0])
        st.markdown(land_use_tab_context[1])
        
        if submitted:
            
            m = folium.Map(**folium_map_kwargs)
            m = display.define_folium_markers(m, marker_stats, session_language=language_choice)
        else:
            # default map data
            m = folium.Map(
                tiles=session_config.map_tiles['url'],
                attr=session_config.map_tiles['html_attribution'],
                location=[47.13, 7.25],
                zoom_start=8,
                min_zoom=7,
                max_zoom=session_config.map_tiles['max_zoom'],
        
                width=700,
                height=400)
            a_popup = FoliumPopup("<div style='min-width:200px; word-break: keep-all;'><h4>Home of good "
                                  "ideas</h4><p>Biel, Switzerland. The home of hammerdirt</p></div>",
                                  show=True)
            folium.Marker(
                location=[47.138784974569866, 7.246126171339943],
                tooltip="Good things happen here!",
                popup=a_popup,
                icon=folium.Icon(icon="cloud"),
    
            ).add_to(m)
        st.markdown("<br />", unsafe_allow_html=True)
            
        st_folium(m, width=725, height=400, returned_objects=[])
        
        
        if submitted:
            
            profile_tab, correlation_tab = st.tabs([profile_of_survey_locations[language_choice],
                                                    correlation_text.correlation_title[language_choice]])
        
            # correlation of land use features
            with correlation_tab:

                luc = display.correlation_matrix(correlation_matrix, language_choice)
                st.markdown(correlation_text.correlation_title[language_choice])
                st.markdown(land_use_correlation[language_choice][0])

                st.write(luc.to_html(escape=False), unsafe_allow_html=True)
                st.markdown("<br />", unsafe_allow_html=True)
                st.markdown(land_use_correlation[language_choice][1])
                st.markdown(land_use_correlation[language_choice][2])

                st.markdown(display.display_columns_to_combine(cor_p, language_choice))

                st.markdown(land_use_correlation[language_choice][3])

            with profile_tab:

                st.markdown(land_use_tab_context[2])
                
                displayed = display.landuse_profile(profiled, nsamples=this_report.number_of_samples(),
                                                    session_language=language_choice)
                st.write(displayed.to_html(escape=False), unsafe_allow_html=True)
                st.markdown("<br />", unsafe_allow_html=True)
                st.markdown(land_use_tab_context[3])
                
                displayed_rate = display.litter_rates_per_feature(rated, session_language=language_choice)
                st.write(displayed_rate.to_html(escape=False), unsafe_allow_html=True)
                st.markdown("<br />", unsafe_allow_html=True)
                st.markdown(land_use_tab_context[4])
                
    with predictions_tab:
        st.write("Predictions tab")



if __name__ == "__main__":
    main()
