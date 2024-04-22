import folium
from folium import Marker
from folium.plugins import MarkerCluster
import pandas as pd

import geospatial
import session_config
from session_config import session_language
import datetime as dt
import matplotlib as mpl
from matplotlib.colors import ListedColormap
import numpy as np

from bokeh.plotting import figure
from session_config import data_directory, code_definitions_c, unpack_with_pandas
from session_config import corr_threshold

# the material and definitions for each code are on
# on a different table. In this instance we call the
# session config to get the data for codes and the lat
# lon data for the beaches
codes = unpack_with_pandas((".", data_directory, code_definitions_c))
code_definitions_map = codes[['code', 'en', 'fr', 'de']].set_index('code')
code_material = codes[['code', 'material']].set_index('code')

beaches = unpack_with_pandas((".", data_directory, session_config.geo_data))
lat_lon = beaches[['slug', 'latitude', 'longitude']].set_index('slug')
f_names = beaches[['feature_name', 'display_feature_name']].drop_duplicates().set_index('feature_name')

# definitions for charts and tables
land_use_map = {
    'en': {
        'orchards': 'Orchards',
        'vineyards': 'Vineyards',
        'buildings': 'Buildings',
        'forest': 'Forest',
        'undefined': 'Undefined',
        'public services': 'Public Services',
        'streets': 'Streets'
    },
    'fr': {
        'orchards': 'Vergers',
        'vineyards': 'Vignobles',
        'buildings': 'Bâtiments',
        'forest': 'Forêt',
        'undefined': 'Non défini',
        'public services': 'Services publics',
        'streets': 'Rues'
    },
    'de': {
        'orchards': 'Obstgärten',
        'vineyards': 'Weinberge',
        'buildings': 'Gebäude',
        'forest': 'Wald',
        'undefined': 'undefiniert',
        'public services': 'öffentliche Dienste',
        'streets': 'Strassen'
    }
}

theme_map = {
    'en': {
        'canton': 'Canton',
        'city': 'Municipality',
        'parent_boundary': 'River basin',
        'r': 'River',
        'l': 'Lake',
        'p': 'Park'
    },
    'fr': {
        'canton': 'Canton',
        'city': 'Municipalité',
        'parent_boundary': 'Bassin versant',
        'r': 'Rivière',
        'l': 'Lac',
        'p': 'Parc'
    },
    'de': {
        'canton': 'Kanton',
        'city': 'Gemeinde',
        'parent_boundary': 'Flusseinzugsgebiet',
        'r': 'Fluss',
        'l': 'See',
        'p': 'Park'
    }}

display_units = {
    'en': 'pcs/m',
    'fr': 'pcs/m',
    'de': 'Stk/m'
}

w_sampling_results = {
    "en": {
        'title': 'Summary of selected data',
        'total': 'Total number of objects',
        'nsamples': 'Number of samples',
        'average': 'Average sample count',
        'quantiles': f'Observed distribution of {display_units[session_language]}',
        'start': 'Date of first sample',
        'end': 'Date of last sample'
    },
    "fr": {
        'title': 'Résumé des données sélectionnées',
        'total': 'Nombre total d\'objets',
        'nsamples': 'Nombre d\'échantillons',
        'average': 'Moyenne par mètre',
        'quantiles': f'Distribution observée des {display_units[session_language]}',
        'start': 'premier échantillon',
        'end': 'dernier échantillon'
    },
    "de": {
        'title': 'Zusammenfassung der ausgewählten Daten',
        'total': 'Abfallobjekte',
        'nsamples': 'Erhebungen',
        'average': 'Durchschnitt pro Meter',
        'quantiles': f'Beobachtete Verteilung der {display_units[session_language]}',
        'start': 'erste Probe',
        'end': 'letzte Probe'}
}

w_admin_boundaries = {
    'en': {
        'title': 'Administrative boundaries',
        'count': 'Count',
        'city' : 'Cities',
        'canton': 'Cantons',
        'parent_boundary': 'River basins or Parks',
        'location': 'Survey locations'
    },
    'fr': {
        'title': 'Limites administratives',
        'count': 'Compter',
        'city': 'Villes',
        'canton': 'Cantons',
        'parent_boundary': 'Bassins versants ou parcs',
        'location': 'Sites d\'enquête'
    },
    'de': {
        'title': 'Verwaltungsgrenzen',
        'count': 'Zählen',
        'city': 'Städte',
        'canton': 'Kantone',
        'parent_boundary': 'Flussgebiete oder Parks',
        'location': 'Untersuchungsstandorte',
    }}

w_feature_inventory = {
    'en': {
        'title': 'Features surveyed',
        'count': 'Count',
        'l': 'Lakes',
        'p': 'Parks',
        'r': 'Rivers',
    },
    'fr': {
        'title': 'Fonctionnalités étudiées',
        'count': 'Compte',
        'l': 'Lacs',
        'p': 'Parcs',
        'r': 'Rivières',
    },
    'de': {
        'title': 'Untersuchte Funktionen',
        'count': 'Zählen',
        'l': 'Seen',
        'p': 'Parks',
        'r': 'Flüsse',
    }
}

material_languages = {
    'en': {
        'plastic': 'Plastic',
        'metal': 'Metal',
        'glass': 'Glass',
        'paper': 'Paper',
        'wood': 'Wood',
        'unidentified': 'Unidentified',
        'chemicals': 'Chemicals',
        'rubber': 'Rubber',
        'cloth': 'Cloth',
    },
    'fr': {
        'plastic': 'Plastique',
        'metal': 'Métal',
        'glass': 'Verre',
        'paper': 'Papier',
        'wood': 'Bois',
        'unidentified': 'Non identifié',
        'chemicals': 'Produits chimiques',
        'rubber': 'Caoutchouc',
        'cloth': 'Tissu',
    },
    'de': {
        'plastic': 'Plastik',
        'metal': 'Metall',
        'glass': 'Glas',
        'paper': 'Papier',
        'wood': 'Holz',
        'unidentified': 'Ubekannt',
        'chemicals': 'Chemikalien',
        'rubber': 'Gummi',
        'cloth': 'Stoff',
    },
}

# the formatting for pd.styler
format_kwargs = dict(precision=2, thousands="'", decimal=",")

# this defines the css rules for the table displays
header_row = {'selector':'th', 'props': f'background-color: #FFF; font-size:12px; text-align:left; width: auto; word-break: keep-all;'}
even_rows = {"selector": 'tr:nth-child(even)', 'props': f'background-color: rgba(139, 69, 19, 0.08);'}
odd_rows = {'selector': 'tr:nth-child(odd)', 'props': 'background: #FFF;'}
table_font = {'selector': 'tr', 'props': 'font-size: 10px;'}
table_data = {'selector': 'td', 'props': 'padding:4px; font-size:12px;text-align: center;'}
table_caption = {'selector': 'caption', 'props': 'caption-side: bottom; font-size:1em; text-align: left;'}
table_caption_top = {'selector': 'caption', 'props': 'caption-side: top; font-size:1em; text-align: left; margin-bottom: 10px;'}
caption_css = {'selector': 'caption', 'props': 'caption-side: top; font-size:.9em; text-align: left; font-style: italic; color: #000;'}
table_first_column_left = {'selector': 'td:nth-child(1)', 'props': 'text-align: left;'}
table_css_styles = [even_rows, odd_rows, table_font, header_row, table_data, table_caption]
highlight_props = 'background-color:#FAE8E8'

# a color gradient for heat maps
# this uses a mix and resamples between 0 and 1
# change the colors  or substitute a  valid matplotlib colormap
top = mpl.colormaps['Oranges'].resampled(2000)
bottom = mpl.colormaps['Greys'].resampled(2000)

newcolors = np.vstack((bottom(np.linspace(0, 1, 2000)),
                   top(np.linspace(0, 1, 2000))))
newcmp = ListedColormap(newcolors, name='OrangeBlue')

a_cmap = newcmp(np.arange(newcmp.N))
a_cmap[:, -1] = np.linspace(0, 1, newcmp.N)

# hour color map should be type matplotlib.colors.ListedColormap
newcmp = ListedColormap(a_cmap)


def display_sampling_result_summary(data: dict, session_language: str, texts: dict = w_sampling_results):
    """Display the sampling results summary"""

    data_labels = texts[session_language]

    to_display = ""

    for akey in ['nsamples', 'total', 'average']:
        to_display += f"* {data_labels[akey]}: {round(data[akey], 2)}\n"
    for akey in ['start', 'end']:
        the_date = dt.datetime.strftime(data[akey], session_config.date_format)
        to_display += f"* {data_labels[akey]}: {the_date}\n"

    display_observed_quantiles = ""
    for akey in ['quantiles']:
        pcts_as_string = ['{:.0%}'.format(x) for x in session_config.report_quantiles]
        data_to_string = [str(round(x, 2)) for i, x in enumerate(data[akey])]
        combined = [f'{pcts_as_string[i]}: {data_to_string[i]}' for i in range(len(pcts_as_string))]
        for value in combined:
            display_observed_quantiles += f"* {value}\n"

    return f"__{data_labels['title']}__", to_display, f"__{data_labels['quantiles']}__", display_observed_quantiles


def display_boundaries(data: dict, session_language: str):
    """Display the administrative boundaries"""
    to_display_boundaries = ""
    for key in data.keys():
        to_display_boundaries += f"* {w_admin_boundaries[session_language][key]}: {data[key]['count']}\n"
    
    return f'__{w_admin_boundaries[session_language]["title"]}__\n {to_display_boundaries}\n'


def feature_inventory(data: dict, session_language: str = 'de'):
    """Display the feature inventory"""
    to_display_features = ""
    for key in data.keys():
        to_display_features += f"* {w_feature_inventory[session_language][key]}: {data[key]['count']}\n"
        
    return f'__{w_feature_inventory[session_language]["title"]}__\n {to_display_features}\n'


default_chart_args = dict(
        title='Sample totals',
        x_axis_type="datetime",
        x_axis_label='date',
        y_axis_label='pcs/m',
        sizing_mode="fixed", width=400, height=400
    )

chart_args_languages = {
    'en': dict(
        title='Sample totals',
        x_axis_type="datetime",
        x_axis_label='date',
        y_axis_label='pcs/m',
        sizing_mode="fixed", width=400, height=400
    ),
    'fr': dict(
        title='Total par échantillon',
        x_axis_type="datetime",
        x_axis_label='date',
        y_axis_label='pcs/m',
        sizing_mode="fixed", width=400, height=400
    ),
    'de': dict(
        title='Stichproben',
        x_axis_type="datetime",
        x_axis_label='Datum',
        y_axis_label='Stk/m',
        sizing_mode="fixed", width=400, height=400
    )
}

most_common_columns = {
    'en': {
        'code': 'Object',
        'quantity': 'Quantity',
        'pcs/m': 'pcs/m',
        '% of total': '% of total',
        'rate': 'Fail rate'
    },
    'fr': {
        'code': 'Objet',
        'quantity': 'Quantité',
        'pcs/m': 'pcs/m',
        '% of total': '% du total',
        'rate': 'Taux d\'échec'
    },
    'de': {
        'code': 'Objekt',
        'quantity': 'Objekt (St.)',
        'pcs/m': 'Stk/m',
        '% of total': 'Anteil',
        'rate': 'Häufigkeitsrate'
        
    }
    
}

w_no_columns_to_combine = {
    'en': '__No columns to combine:__ Note that a correlation coefficient of 1 or -1 is not considered.',
    'fr': '__Aucune colonne à combiner:__ Notez qu\'un coefficient de corrélation de 1 ou -1 n\'est pas considéré.',
    'de': '__Keine Spalten zum Kombinieren:__ Beachten Sie, dass ein Korrelationskoeffizient von 1 oder -1 nicht '
          'berücksichtigt wird.'
}

w_columns_to_combine = {
    "en": {
        'method': 'Method',
        'new_name': 'New name'
    },
    "fr": {
        'method': 'Méthode',
        'new_name': 'Nouveau nom'
    },
    "de": {
        'method': 'Methode',
        'new_name': 'Neuer Name'
        
    }
}


def scatter_chart_title(units: str = None,  session_language: str = 'en'):
    atitle = chart_args_languages[session_language]['title']
    return f"{atitle} : {units}"


def apply_gradient(palette='RdYlGn9', y: list = None):
    """Apply a gradient to the chart"""
    from bokeh.models import LinearColorMapper
    color_mapper = LinearColorMapper(palette=palette, low=min(y), high=max(y))
    return color_mapper


def scatter_plot(x, y, figure_kwargs: dict = default_chart_args, session_language: str = 'en',
                 gradient: bool = False, palette: str = 'RdYlGn9', categorical: bool = False, data: pd.DataFrame = None):
    """Display the scatter plot"""
    from bokeh.transform import factor_cmap
    from bokeh.models import Scatter
    
    figure_kwargs.update({'title': scatter_chart_title(units=display_units[session_language], session_language=session_language)})
    figure_kwargs.update({'x_axis_label': chart_args_languages[session_language]['x_axis_label']})
    figure_kwargs.update({'y_axis_label': chart_args_languages[session_language]['y_axis_label']})
    p = figure(**figure_kwargs)
    
    if gradient:
        color_mapper = apply_gradient(y=y.values, palette=palette)
        p.x(x, y, color={'field': 'y', 'transform': color_mapper}, legend_label='Trend', size=10, line_width=2)
    elif categorical:
        
        a_cmap = factor_cmap('city', palette='Category10_3', factors=data.city.unique()),
        glyph = Scatter(x='', y='pcs/m', size=12, marker='x')
        p.add(data, glyph)
    else:
        p.x(x, y, legend_label='Sample total', fill_color='dodgerblue', line_width=1, size=12)
    return p


def code_definitions(codes: pd.Series, session_language: str = 'en'):
    
    language_map = code_definitions_map[session_language]
    defined = codes.apply(lambda x: language_map.loc[x])
    return defined

def code_selector(selections: [] = None, session_language: str = 'en'):
    language_map = code_definitions_map[session_language]
    descriptions = [language_map.loc[x] for x in selections[1:]]
    all = {
        'en': 'all',
        'fr': 'tout',
        'de': 'alle'
    }

    return [all[session_language], *descriptions]

def code_selector_to_code_label(a_description: str, session_language: str = 'en'):
    if a_description in ['all', 'tout', 'alle']:
        return a_description
    else:
        language_map = code_definitions_map[session_language]
        return language_map[language_map == a_description].index[0]

    

def most_common(df, session_language: str = 'en'):
    """Display the most common objects"""
    explain = {
        'en': "The most common objects are a combination of the top ten most abundant objects and those objects that "
              "are found in more than 50% of the samples. Some objects are found frequently but at low quantities."
              "Other objects are found in fewer samples but at higher quantities.",
       'fr': "Les objets les plus courants sont une combinaison des dix objets les plus abondants et de ceux qui se "
             "trouvent dans plus de 50% des échantillons. Certains objets sont fréquemment trouvés mais en faibles "
             "quantités. D'autres objets sont trouvés dans moins d'échantillons mais en plus grandes quantités.",
       'de': "Die häufigsten Objekte sind eine Kombination der zehn häufigsten Objekte und derjenigen, die in mehr als "
             "50% der Proben gefunden werden. Einige Objekte werden häufig, aber in geringen Mengen gefunden. Andere "
             "Objekte werden in weniger Proben, aber in größeren Mengen gefunden."
    }

    caption = {
        'en': f"<b>The most common objects from the selected data.</b> {explain['en']}",
        'fr': f"<b>Les objets les plus courants</b> {explain['fr']}",
        'de': f"<b>Die häufigsten Objekte.</b> {explain['de']}"
    }
    
    table_style = [*table_css_styles[:-1], table_caption_top, caption_css, table_first_column_left]
    
    a = df.sort_values('quantity', ascending=False).head(10).code.unique()
    
    b = df[df['rate'] >= 0.5].code.unique()
    data = df[df.code.isin(list({*a, *b}))]
    data = data.sort_values('quantity', ascending=False)
    mc_q = data.quantity.sum()
    pct_total = mc_q / df.quantity.sum()

    data = data[most_common_columns['en'].keys()].copy()
    data['code'] = code_definitions(data['code'], session_language)

    data.rename(columns=most_common_columns[session_language], inplace=True)
    data = data.style.set_table_styles(table_style).set_caption(caption[session_language]).format(**format_kwargs)
    
    return data.hide(axis=0), pct_total


def style_negative(v, props=''):
    """from panaas docs: pandas-docs/version/0.24.2/reference/api/pandas.io.formats.style.Styler.applymap.html"""
    return props if v < 0 else None


def correlation_matrix(df, session_language: str = 'en'):
    """Display the correlation matrix"""
    di = df.style.set_table_styles([table_font])\
        .map(style_negative, props='color: red')\
        .map(lambda n: 'opacity: 20%;' if abs(n) < corr_threshold else None)\
        .format(na_rep='-')
    
    return di


def display_columns_to_combine(columns_to_combine: list, session_language: str = 'en'):
    """Display the columns to combine"""
    list_of_combination = ""
    
    if len(columns_to_combine) == 0:
        return w_no_columns_to_combine[session_language]
    for cols in columns_to_combine:
        method = w_columns_to_combine[session_language]['method']
        new_name = w_columns_to_combine[session_language]['new_name']
        list_of_combination += f"* {cols[0]}, {cols[1]}; {method}: `{cols[2]}`, {new_name}: `{cols[0]}_{cols[1]}`\n"
    
    return list_of_combination


def highlight_max(s, props: str = highlight_props):
    return np.where((s == np.max(s.values)) & (s != 0), props, '')


def landuse_profile(aprofile: pd.DataFrame, session_language: str = 'en', nsamples: int = 0):
    
    """Display the land use profiles"""
    
    explain = {
        'en': "The highlighted cell is the maximum value in the row. Each cell represents the proportion of samples "
              "that were conducted in the land use category.",
        'fr': "La cellule en surbrillance est la valeur maximale de la ligne. Chaque cellule représente la proportion "
              "d'échantillons effectués dans la catégorie d'utilisation des sols.",
        'de': "Die hervorgehobene Zelle ist der Maximalwert in der Zeile. Jede Zelle stellt den Anteil der Proben dar, "
              "die in der Landnutzungskategorie durchgeführt wurden."
    }
    
    caption = {
        'en': f"<b>The land use profile and the proportion of samples per landuse feature.</b> {explain['en']}",
        'fr': f"<b>Le profil d'utilisation des sols et la proportion d'échantillons par catégorie.</b> {explain['fr']}",
        'de': f"<b>Das Landnutzungsprofil und der Anteil der Proben pro Kategorie.</b> {explain['de']}"
    }
    
    f = aprofile/nsamples
    a_new_index = [land_use_map[session_language][x] for x in f.index]
    
    f = f.style.apply(highlight_max, axis=1)
    
    f = f.set_table_styles([table_caption_top, caption_css]).format('{:.0%}')
    f = f.set_caption(caption[session_language])
    f.data = f.data.set_index(pd.Index(a_new_index))
    return f


def litter_rates_per_feature(aresult: pd.DataFrame, session_language: str = 'en'):
    """Display the litter rates per feature"""
    
    explain = {
        'en': "The highlighted cell is the maximum value in the row. Each cell represents the average observed trash "
              "per meter in the land use category.",
        'fr': "La cellule en surbrillance est la valeur maximale de la ligne. Chaque cellule représente le taux moyen de "
              "déchets observé par mètre dans la catégorie d'utilisation des sols.",
        'de': "Die hervorgehobene Zelle ist der Maximalwert in der Zeile. Jede Zelle stellt den durchschnittlichen Müll "
              "pro Meter in der Landnutzungskategorie dar."
    }
    
    caption = {
        'en': f"<b>The land use profile and the observed average litter rates per feature.</b> {explain['en']}",
        'fr': f"<b>Le profil d'utilisation des sols et les taux moyens de déchets observés par fonction.</b> {explain['fr']}",
        'de': f"<b>Das Landnutzungsprofil und die beobachteten durchschnittlichen Müllraten pro Funktion.</b> {explain['de']}"
    }
    column_labels_land_use = geospatial.column_labels_land_use

    d = aresult.loc[session_config.feature_variables].copy()
    d.rename(columns=column_labels_land_use, inplace=True)
    a_new_index = [land_use_map[session_language][x] for x in d.index]
    f = d.style.set_table_styles([table_caption_top, caption_css]).format('{:.2f}')
    f = f.set_caption(caption[session_language])
    f = f.apply(highlight_max, axis=1)
    f.data = f.data.set_index(pd.Index(a_new_index))
    return f


def map_markers(df, lat_lon: pd.DataFrame = lat_lon):
    """Map the markers"""
    nsamples = df.groupby('location', observed=True)['sample_id'].nunique()
    qty_location = df.groupby('location', observed=True)['quantity'].sum()
    rate_location = df.groupby('location', observed=True)['pcs/m'].mean().round(2)
    last_sample = df.groupby('location', observed=True)['date'].max()
    df = pd.concat([nsamples, qty_location, rate_location, last_sample], axis=1)
    df = df.merge(lat_lon, left_index=True, right_index=True)
    df['location'] = df.index
    max_lat, min_lat = df['latitude'].max(), df['latitude'].min()
    max_lon, min_lon = df['longitude'].max(), df['longitude'].min()
    
    return df.to_dict(orient='records'), {'max_lat': max_lat, 'min_lat': min_lat, 'max_lon': max_lon, 'min_lon': min_lon}


def map_pop_up_markers(a_marker, session_language: str = 'en'):
    """Map the pop up markers"""
    language_labels = {
        'en':{
            'location': 'Location',
            'sample_id': 'Samples',
            'quantity': 'Total objects',
            'pcs/m': 'pcs/m',
        },
        'fr': {
            'location': 'Emplacement',
            'sample_id': 'Échantillons',
            'quantity': 'Objets totaux',
            'pcs/m': 'pcs/m',
        },
        'de': {
            'location': 'Ort',
            'sample_id': 'Proben',
            'quantity': 'Gesamtobjekte',
            'pcs/m': 'Stk/m',
        }
        
    }
    loc_list = f'<li>{language_labels[session_language]["location"]} : {a_marker["location"]}</li>'
    n_samples = f'<li>{language_labels[session_language]["sample_id"]} : {a_marker["sample_id"]}</li>'
    quantity = f'<li>{language_labels[session_language]["quantity"]} : {"{:,}".format(a_marker["quantity"])}</li>'
    pcs_meter = f'<li>{language_labels[session_language]["pcs/m"]} : {a_marker["pcs/m"]}</li>'
    
    return f"<div style='min-width:300px; word-break: keep-all;'><ul>{loc_list}{n_samples}{quantity}{pcs_meter}</ul></div>"


def define_folium_markers(m: folium.Map, marker_data: [] = None,  session_language: str = 'en'):
    """Define the folium markers"""

    marker_cluster = MarkerCluster().add_to(m)
    
    for a_marker in marker_data:
        popup = map_pop_up_markers(a_marker, session_language=session_language)
        marker = Marker(location=[a_marker['latitude'], a_marker['longitude']], popup=popup)
        marker.add_to(marker_cluster)
    return m

def object_summary(df, session_language: str = 'en'):
    """Display the object summary"""
    explain = {
        'en': "The inventory details the total quantity, average pcs/m, % of total and fail rate for each object identified "
              "in the report.",
        'fr': "L'inventaire détaille la quantité totale, la moyenne des pcs/m, le % du total et le taux d'échec pour chaque "
                "objet identifié dans le rapport.",
        'de': "Das Inventar enthält die Gesamtmenge, den durchschnittlichen Stückpreis, den Prozentsatz des Gesamtwerts "
                "und die Ausfallrate für jedes im Bericht identifizierte Objekt."
    }

    caption = {
        'en': f"<b>The inventory.</b> {explain['en']}",
        'fr': f"<b>L'inventaire</b> {explain['fr']}",
        'de': f"<b>Das Inventar</b> {explain['de']}"
    }

    a_new_index = [code_definitions_map[session_language].loc[x] for x in df.code]
    table_style = [*table_css_styles[:-1], table_caption_top, caption_css, table_first_column_left]

    df["% of total"] = df["% of total"].map(lambda x: '{:.0%}'.format(x))

    df["rate"] = df["rate"].map(lambda x: '{:.0%}'.format(x))
    df['code'] = a_new_index
    df = df[['code', 'quantity', 'pcs/m', '% of total', 'rate']]
    df = df.sort_values('quantity', ascending=False)
    df.rename(columns=most_common_columns[session_language], inplace=True)
    f = df.style.set_table_styles(table_style).format(**format_kwargs)
    f = f.set_caption(caption[session_language])


    return f.hide(axis=0)

def landuse_catalog(df, session_language: str = 'en'):
    """Display the land use catalog"""
    explain = {
        'en': "The land use catalog details the magnitude of land each land use category for each location, was well as "
              "the average pcs/m for the location",
        'fr': "Le catalogue d'utilisation des terres détaille la quantité de terre de chaque catégorie d'utilisation des "
              "terres pour chaque emplacement, ainsi que la moyenne des pcs/m pour l'emplacement.",
        'de': "Der Landnutzungskatalog gibt die Größe des Landes für jede Landnutzungskategorie für jeden Standort an, "
              "sowie den durchschnittlichen Stückpreis für den Standort."
    }

    caption = {
        'en': f"<b>The land use catalog.</b> {explain['en']}",
        'fr': f"<b>Le catalogue d'utilisation des terres.</b> {explain['fr']}",
        'de': f"<b>Der Landnutzungskatalog.</b> {explain['de']}"
    }

    table_style = [*table_css_styles[:-1], table_caption_top, caption_css, table_first_column_left]

    df = df.sort_values('pcs/m', ascending=False)
    df['pcs/m'] = df['pcs/m'].round(2)
    df.rename(columns=land_use_map[session_language], inplace=True)
    f = df.style.set_table_styles(table_style)
    f.map(lambda x: 'color: #E5E5E5' if pd.isnull(x) else '')
    f.map(lambda x: 'background: #E5E5E5' if pd.isnull(x) else '')
    f.format({**format_kwargs})

    f = f.set_caption(caption[session_language])

    return f.hide(axis=0)


def buffer_pcs_m(m: folium.Map, marker_data: [] = None, df: pd.DataFrame = None, session_language: str = 'en'):
    # """Buffer the pcs/m"""
    # for a_marker in marker_data:
    #
    #     radius = a_marker['pcs/m']
    #     folium.Circle(
    #         location=[a_marker['latitude'], a_marker['longitude']],
    #         radius=radius,
    #         color="black",
    #         weight=1,
    #         fill_opacity=0.6,
    #         opacity=1,
    #         fill_color="green",
    #         fill=False,
    #         popup="{} meters".format(radius),
    #         tooltip="I am in meters",
    #     ).add_to(m)
    # return m
    pass
