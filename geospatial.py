import pandas as pd
from sklearn.preprocessing import MinMaxScaler

import session_config
from session_config import feature_variables
from session_config import object_of_interest
from session_config import index_label, location_label, Y, Q
from session_config import agg_groups


landuse = pd.read_csv('data/land_use.csv')
landcover = pd.read_csv('data/land_cover.csv')
streets = pd.read_csv('data/streets.csv')
river_intersects = pd.read_csv('data/river_intersect_lakes.csv')



words_land_use_profile = {
    'en': 'Percent of land attributed v/s % of samples',
    'fr': 'Pourcentage d\'occupation du sol v/s % d\'échantillons',
    'de': 'Prozent des Landes zugeschrieben v/s % der Proben'
}

words_land_use_litter_rates = {
    'en': 'Percent of land attributed v/s trash per meter of shoreline',
    'fr': 'Pourcentage d\'occupation du sol v/s déchets par mètre de rivage',
    'de': 'Prozent des Landes zugeschrieben v/s Stück Müll pro Meter Ufer'
}

column_labels_land_use = {
    1: '> 0 - 20%',
    2: '20 - 40%',
    3: '40 - 60%',
    4: '60 - 80%',
    5: '80 - 100%'
}


def select_x_and_y(df_target, features, x_value: str = 'scale'):
    """Selects the feature columns and the target column from the DataFrame"""

    for label in ['public services', 'streets']:
        df_target[label] = df_target.location.apply(lambda x: features[label].loc[x, x_value])

    for label in ['landcover']:
        df = df_target.merge(features[label], left_on=location_label, right_on=location_label, how='left')
    for label in ['river_intersects']:
        if len(features[label]) == 0:
            return df
        else:
            df_rivers = df_target.merge(features[label], left_on=location_label, right_on=location_label, how='left')
            return df, df_rivers

def categorize_features(df, feature_columns=feature_variables):
    """Categorizes the feature columns in the DataFrame"""
    bins = session_config.bins
    labels = session_config.bin_labels
    for column in feature_columns:
        df[column] = pd.cut(df[column], bins=bins, labels=labels)
    return df


def category_quantiles(df, feature, category):
    return df[df[feature] == category].groupby([feature]).agg(agg_groups)


def scale_combined(df, column_to_scale, new_column_name):
    """Scales the combined columns"""
    scaler = MinMaxScaler()
    df[new_column_name] = scaler.fit_transform(df[[column_to_scale]])
    return df


def collect_topo_data(locations: [] = None, labels: {} = None):
    """Collects the topographical data"""

    d_t_c = {
        'public services': landuse.rename(columns={'slug': location_label}),
        'landcover': landcover.rename(columns={'slug': location_label}),
        'streets': streets.rename(columns={'slug': location_label}),
        'river_intersects': river_intersects.rename(columns={'slug': location_label})
    }

    if labels is None:
        if locations is None:
            return d_t_c
        else:
            strts = d_t_c['streets'].copy()
            strts = strts.groupby(location_label)[['length']].sum().reset_index()
            strts = scale_combined(strts, 'length', 'scale')
            strts.set_index(location_label, inplace=True, drop=True)

            ps = d_t_c['public services'].copy()
            ps = ps.groupby(location_label).agg({'scale': 'sum', 'area': 'sum'})

            lc = d_t_c['landcover'].copy()
            lc = lc.pivot(index=location_label, columns='attribute', values='scale').reset_index()
            new_columns = {'Siedl': 'buildings', 'Wald': 'forest', 'Reben': 'vineyards', 'Obstanlage': 'orchards'}
            lc.rename(columns=new_columns, inplace=True)

            d_t_c.update({'streets': strts, 'public services': ps, 'landcover': lc})

            return d_t_c
    else:
        return labels
    

def unscale_land_use(df, feature_columns=feature_variables):
    """Unscales the land use features"""
    for column in feature_columns:
        df[f'{column}_m'] = df[column] * session_config.buffer_area
    
    return df


def combine_landuse_features(data, columns_to_combine: list = None, new_column_name: str = None, method: str = 'sum'):
    """Combines the columns in the DataFrame
    
    The columns are put back into m² before combining. Then scaled back.
    """
    if method == 'sum':
        data = unscale_land_use(data, feature_columns=columns_to_combine)
        data[new_column_name] = data[columns_to_combine[0]] + data[columns_to_combine[1]]
        data[new_column_name] = data[new_column_name] / session_config.buffer_area
        data = scale_combined(data, new_column_name, new_column_name)
        columns_to_drop = [f'{x}_m' for x in columns_to_combine]
        data.drop(columns=columns_to_drop, inplace=True, axis=1)
        
        return data
    if method == 'rate':
        not_public_services = [x for x in columns_to_combine if 'public services' not in x]
        data = unscale_land_use(data, feature_columns=columns_to_combine)
        data[new_column_name] = (data['public services']*data[not_public_services[0]]).round(3)
        data = scale_combined(data, new_column_name, new_column_name)
        columns_to_drop = [f'{x}_m' for x in columns_to_combine]
        data.drop(columns=columns_to_drop, inplace=True, axis=1)
        
        return data
    
    else:
        return "Method not recognized. Please use 'sum' or 'rate' as the method."
    

def find_correlated_values(df, threshold: float = session_config.corr_threshold):
    """Finds the correlated values in the DataFrame"""
    
    labels = df.columns.to_list()
    correlated_features = []
    for i in range(len(labels)):
        for j in range(i+1, len(labels)):
            if df.at[labels[i], labels[j]] >= .99999:
                pass
            elif df.at[labels[i], labels[j]] <= 0:
                pass
            elif df.at[labels[j], labels[i]] <= 0:
                pass
            elif df.at[labels[i], labels[j]] >= threshold:
                correlated_features.append((labels[i], labels[j]))
         
    return correlated_features


def make_multi_index(column_labels: dict, group_label: dict, nlabels: int, session_language: str = 'en'):
    """Creates a multi index for the DataFrame"""
    ""
    indexes = [(group_label[session_language], column_labels[x]) for x in range(1, nlabels+1)]
    
    return pd.MultiIndex.from_tuples(indexes)


def the_land_use_profile(df, feature_columns: [] = session_config.feature_variables,
                         session_language: str = 'en'):
    """Creates a profile of the land use data"""

    # avg_matrix = pd.DataFrame(index=session_config.feature_variables, columns=session_config.bin_labels)
    #
    # d = df.copy()
    #
    # # Calculate the mean for each category in each identified column
    # for column in session_config.feature_variables:
    #     for category in session_config.bin_labels:
    #         # Filter df by category and calculate mean for the target variable, only if it's relevant
    #         filtered = df[df[column] == category]
    #         avg_matrix.at[column, category] = filtered[Y].mean() if not filtered.empty else 0
    #
    # return avg_matrix.round(2)
    
    d = df[feature_columns].copy()
    d = d.T
    # indexes = [(words_land_use_profile[session_language], column_labels[x]) for x in range(1, len(df) + 1)]
    column_index = make_multi_index(column_labels_land_use, words_land_use_profile, len(df), session_language)
    d.columns = column_index
    
    return d


def the_litter_rate_per_land_use(df, feature_columns: [] = session_config.feature_variables,
                                 session_language: str = 'en'):
    """Creates a profile of the litter rate per land use data"""
    
    # d = df[feature_columns].copy()
    # d = d.T
    # column_index = make_multi_index(column_labels_land_use, words_land_use_litter_rates, len(df), session_language)
    # d.columns = column_index
    # column_index = make_multi_index(column_labels_land_use, words_land_use_profile, len(df), session_language)
    # df.columns = column_index
    
    return df


class ALandUseObject:

    def __init__(self, locations, df_feature):
        self.locations = locations
        self.feature_df = df_feature

    def n_samples(self):
        return self.df[index_label].nunique()

    def n_pieces(self):
        return self.df[Q].sum()

    def locations(self):
        return self.df[location_label].nunique()

    def summary_results_by_category(self):
        results = {}
        for i in self.df[self.feature].unique():
            results.update({i: category_quantiles(self.df, self.feature, i)})

        return results

    def results_by_category(self, category):
        return self.df[self.df[self.feature] == category]

    def summary_y(self):
        asummary = dict(
            n_samples=self.n_samples(),
            n_locations=self.locations(),
            total=self.n_pieces(),
            quantiles=self.summary_results_by_category()
        )
        return asummary


class LandUseReport:

    def __init__(self, df_target, features):
        self.target = df_target
        self.features = features
        self.feature_variables = list(self.features.keys())
        self.intersects = None
        self.df_cat = None
        self.merge_land_use_to_survey_data()

    def merge_land_use_to_survey_data(self):
        lu = select_x_and_y(self.target, self.features)
        if len(lu) == 2:
            self.df_cont, self.intersects = lu
        else:
            self.df_cont = lu
        
    def categorize_columns(self, df, feature_columns=feature_variables):
        return categorize_features(df, feature_columns=feature_columns)

    def n_samples_per_feature(self):
        df_feature = {feature: self.df_cat[feature].value_counts() for feature in
                      self.feature_variables}
        df_concat = pd.concat(df_feature, axis=1)
        return df_concat.fillna(0).astype('int')

    def n_pieces_per_feature(self):
        df_feature = {feature: self.df_cat.groupby(feature, observed=True)[Q].sum() for feature in
                      self.feature_variables}
        df_concat = pd.concat(df_feature, axis=1)
        return df_concat.fillna(0).astype('int')

    def locations_per_feature(self):
        df_feature = {feature: self.df_cat.groupby(feature, observed=True)[location_label].nunique() for feature in
                      self.feature_variables}
        df_concat = pd.concat(df_feature, axis=1)
        return df_concat.fillna(0).astype('int')

    def rate_per_feature(self, afunc: str = session_config.tendencies):

        avg_matrix = pd.DataFrame(index=self.feature_variables, columns=session_config.bin_labels)

        df = self.df_cat.copy()

        # Calculate the mean for each category in each identified column
        for column in self.feature_variables:
            for category in session_config.bin_labels:
                # Filter df by category and calculate mean for the target variable, only if it's relevant
                filtered = df[df[column] == category]
                avg_matrix.at[column, category] = filtered[Y].mean() if not filtered.empty else 0

        return avg_matrix.round(2)
    
    def combine_features(self, columns_to_combine: list = session_config.default_args):
        
        d = self.df_cont.copy()
        new_names = []
        for cols in columns_to_combine:
            new_column_name = f'{cols[0]}_{cols[1]}'
            new_names.append(new_column_name)
            d = combine_landuse_features(d, columns_to_combine=[cols[0], cols[1]], new_column_name=new_column_name, method=cols[2])
        self.df_cont = d
        new_feature_columns = [*feature_variables, *new_names]
        self.feature_variables = new_feature_columns
        self.df_cat = self.categorize_columns(d.copy(), feature_columns=new_feature_columns)
        return new_feature_columns

    def correlation_matrix(self):

        return self.df_cont[feature_variables].corr()
    
    def assign_combination_method(self, pairs):
        
        if len(pairs) == 0:
            return []
        pairs_methods = []
        for pair in pairs:
            if 'public services' in pair:
                new_pair = (*pair, 'rate')
                pairs_methods.append(new_pair)
            else:
                new_pair = (*pair, 'sum')
                pairs_methods.append(new_pair)
        return pairs_methods
     
    def correlated_pairs(self, threshold: float = session_config.corr_threshold):
        
        d = self.correlation_matrix()
        d = d[[x for x in d.columns if x != 'streets']].fillna(1)
        c_p = find_correlated_values(d, threshold=threshold)
        
        return self.assign_combination_method(c_p)
    
    def report_by_feature(self, feature):

        return ALandUseObject(self.df_cat, feature, object_of_interest, Y)




