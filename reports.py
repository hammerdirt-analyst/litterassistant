import pandas
import pandas as pd
import numpy as np

import geospatial
from session_config import administrative, feature_variables, feature_types, columns
from session_config import object_of_interest
from session_config import index_label, location_label, Y, Q
from session_config import unit_agg, agg_groups
from session_config import report_quantiles


def select_features(df, column, labels):
    mask = df[column].isin(labels)
    return df[mask]


def select_dates(df, start_end):
    mask = (df['date'] >= start_end[0]) & (df['date'] <= start_end[1])
    return df[mask]


def collect_sample_totals(df, sample_id: str = 'sample_id', location_label: str = location_label,
                          info_columns: list = None, afunc: {} = unit_agg):
    # a sample total is the sum of all the codes with the same sample Id. The code column is identified
    # with the object_of_interest variable
    if not info_columns:
        return df.groupby([sample_id, location_label, 'date'], as_index=False).agg(afunc)
    else:
        return df.groupby([sample_id, location_label, 'date', *info_columns], as_index=False).agg(afunc)


def collect_aggregate_values(df, column: str = None, funcs: {} = agg_groups):
    
    return df.groupby(column).agg(funcs)


# # combining feature labels
# # reducing dimensions
# # good for combining object classes into use groups

# # method to group feature labels before applying any other methods
# # here we are using the groups from the plastock project. The tuple
# # starts with the feature to be combined, then an array of the labels
# # to combine and the then the value attributed to the new label.
# or [<column name>, <list of labels to combine>, <new label name>]
default_groups = [
        ('code', ['G22', 'G23', 'G24'], 'Gcaps'),
]



def combine_feature_labels(df, feature: str, labels_to_combine: list, new_label_name: str) -> pd.DataFrame:
    """Combines the feature labels of one series of features. accepts a pd.DataFrame"""
    try:
        df.loc[df[feature].isin(labels_to_combine), feature] = new_label_name
        return df
    except Exception as e:
        statement = "That combination of variables did not work. See below."
        print(f'{statement}\n{e}')
    
    finally:
        return df


def reduce_dimensionality_observed(df, groups: list) -> pd.DataFrame:
    for agroup in groups:
        df = combine_feature_labels(df, *agroup)
    df.groupby(columns, as_index=False).agg(unit_agg)
    return df


class AReport:
    
    def __init__(self, dfc):
        self.df = dfc
        
    def administrative_boundaries(self):
        """Returns the name and number of unique Cantons and Cities in a report"""
        result = {}
        for boundary in administrative:
            names = self.df[boundary].unique()
            result.update({boundary: {'count': len(names), 'names': names}})
        
        return result

    def feature_inventory(self):
        """Returns the name and number of geographic boundaries in a report. River bassin, lake park etc.."""
        result = {}
        for feature_type in feature_types:
            unique_features = self.df[self.df['feature_type'] == feature_type]['feature_name'].unique()
            if unique_features.size == 0:
                result[feature_type] = {
                    'count': 0,
                    'names': None
                }
            else:
                result[feature_type] = {
                    'count': len(unique_features),
                    'names': unique_features.tolist()
                }
        return result

    def date_range(self):
        """The date range of the selected results"""
        start = self.df['date'].min()
        end = self.df['date'].max()
        return {'start': start, 'end': end}
    
    def inventory(self):
        """Returns the total quantity, median pcs/m, % of total and fail rate for each object code in the report"""
        tq = self.total_quantity()
        # dask_df = dd.from_pandas(self.df, npartitions=1)
        object_totals = self.df.groupby(object_of_interest).agg(agg_groups)
        object_totals['% of total'] = object_totals[Q]/tq
        
        return object_totals

    def total_quantity(self):
        """Returns the total quantity of the report"""
        return self.df[Q].sum()
    
    def number_of_samples(self):
        """Returns the number of unique sample_ids in the report"""
        return self.df.sample_id.nunique()

    def fail_rate(self, threshold: int = 1):
        rates = self.df.groupby([object_of_interest])[index_label].nunique().reset_index()
        for anobject in rates[object_of_interest].unique():
            nfails = sum((self.df[object_of_interest] == anobject) & (self.df[Q] >= threshold))
            n_anobject = rates.loc[rates[object_of_interest] == anobject, index_label].values[0]
            rates.loc[rates[object_of_interest] == anobject, ['fails', 'rate']] = [nfails, nfails/n_anobject]

        return rates

    def sample_results(self, df: pandas.DataFrame = None, **kwargs):
        """The sample totals for the date range of the selected results"""

        if not df:
            return collect_sample_totals(self.df.copy(), **kwargs)
        else:
            return collect_sample_totals(df.copy(), **kwargs)

    def sampling_results_summary(self):
        """The summary of the sample totals"""

        data = self.sample_results()[Y].values
        qtiles = np.quantile(data, report_quantiles)
        average = np.mean(data)
        total = self.inventory()[Q].sum()
        nsamples = self.number_of_samples()
        date_range = self.date_range()

        return {'total': total, 'nsamples': nsamples, 'average': average, 'quantiles': qtiles, 'start': date_range['start'], 'end': date_range['end']}

    def object_summary(self):
        qtys = self.inventory()
        return qtys.merge(self.fail_rate(), right_on=object_of_interest, left_on=object_of_interest)
    
    def sampling_conditions(self):
        """Returns the land use profile of the data"""

        locations = self.df[location_label].unique()

        topo_data = geospatial.collect_topo_data(locations=locations)
        return topo_data

