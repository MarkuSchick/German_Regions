""" aggregate over districts """
import pandas as pd
from unidecode import unidecode

from config import DATA_DISTRICTS, DATA_MAPPINGS, DATA_MUNICIPALITIES


def aggregate_district_data(year):
    """ Aggregates the municipality do the district levels and merges on the name of the district.
        Saves the district dataset as csv
    Args:
        year: year of municipality data
    """

    # load in municipality dataset
    municipality_df = pd.read_csv(DATA_MUNICIPALITIES / r"municipalities_{}.csv".format(year), index_col = "index")
    

    # aggregate over districts
    district_df = municipality_df.groupby(["state", "gov_district", "district"])[["pop_total", "area_km2"]].sum()
    district_df["density"] = district_df["pop_total"].div(district_df["area_km2"])

    # map on district names
    district_mapping =  pd.read_csv(DATA_MAPPINGS / r"district_{}.csv".format(year), index_col = ["district","gov_district","state"])
    district_df = district_df.merge(district_mapping, left_index = True, right_index = True)

    # convert german umlaut to ascii character
    district_df['district_name_ascii'] = district_df['district_name'].apply(lambda x: unidecode(x)) 

    # sort district dataset  
    district_df = district_df.sort_values(["state", "gov_district", "district"])

    # save district file
    district_df.to_csv(path_or_buf = DATA_DISTRICTS / "districts_{}.csv".format(year), index=True)

