import pandas as pd

from config import DATA, DATA_MAPPINGS, DATA_MISC, DATA_MUNICIPALITIES, DATA_RAW


def load_excel_data(year):
    """ loads raw excel downloaded from destatis and returns as dataframe
    Args:
        year: current year
    """
    
    # handle varying nameing of excel sheets in given years
    if year < 1993:
        data_sheet = "31.12.{}".format(year)
    elif year >= 1993 and year < 2014:
        data_sheet = "Gemeindedaten"
    elif year >= 2014:
        data_sheet = "Onlineprodukt_Gemeinden_3112{}".format(str(year)[2:])
    else:
        assert False, "Sheet name with municipality data in year {} is unknown".format(year)
    

    # read in data 
    df = pd.read_excel(DATA_RAW / r"municipalities{}.xls".format(year), 
    sheet_name=data_sheet, header = None)
    
    # exctract column names from first 5 rows

    # translate first keys with literal string
    includes_expected_header = df.loc[0:5,:].isin(["Land", "RB", "Kreis", "VB", "Gem", "Gemeindename", "insgesamt", "je km2"])
    mat = df.loc[0:5, : ][includes_expected_header].dropna(axis='columns', how='all') # keep columns which include above column names
    translate_dict = {old_column_name: mat.loc[:, old_column_name].dropna().values[0] for old_column_name in mat.columns} 
    df = df.rename(columns = translate_dict) # rename the default column names (0,1,2,...) => ("Land", "Kreis", ....)
    
    # translate square kilo meter with contain statement
    includes_square_meter = df.loc[0:5].apply(lambda x: x.str.contains("km2"))
    mat = df.loc[0:5, : ][includes_square_meter].dropna(axis='columns', how='all') # keep columns which include above column names
    translate_dict = {old_column_name: "Fläche km2" for old_column_name in mat.columns if type(old_column_name)==int} 
    df = df.rename(columns = translate_dict) # rename the default column names (0,1,2,...) => ("Land", "Kreis", ....)
    
    
    df = df.loc[6:] # drop columns with meta information

    # rename columns and select interesting once 
    df = df.rename(
        columns = {
        "Land": "state", 
        "RB": "gov_district", 
        "Kreis": "district", 
        "VB": "municipality_assoc", 
        "Gem": "municipality", 
        "Gemeindename": "municipality_name",
        "Fläche km2": "area_km2",
        "insgesamt": "pop_total",
        "je km2": "pop_density"
        }
        )
    
    keep_columns = ["state", "gov_district", "district", "municipality_assoc", "municipality", "municipality_name", "area_km2", "pop_total", "pop_density"]
    df = df[[column for column in df.columns if column in keep_columns]] # keep only renamed columns
    df =  df.dropna(axis="index", how="all") # drop text after table
    return df 

def get_relative_level(data_columns, region_level):
    """ determine relative level of region level in current wave 
    return: all strictly lower levels, all weakly stronger level
    """
    regional_level_categories = pd.Categorical(["municipality", "municipality_assoc", "district", "gov_district", "state"], 
                                            ordered=True, categories=["municipality", "municipality_assoc", "district", "gov_district", "state"])

    lower_levels = regional_level_categories[regional_level_categories<region_level] # strictly lower regional levels
    lower_levels = [levels for levels in lower_levels if levels in data_columns] # keep only levels included in wave

    higher_levels = regional_level_categories[regional_level_categories>=region_level] # weakly higher regional levels
    higher_levels = [levels for levels in higher_levels if levels in data_columns] # keep only levels included in wave

    return higher_levels, lower_levels


def get_region_level_index(data, region_level, lower_levels, higher_levels):
    """ Identifies the name of the regional levels and returns the index
    Logic: 
    The row with a district has higher levels coded while lower levels (and district + municipality_name) are missing

    Args: 
        regional_level_name: Name of regional level in dataset
        higher_regional_level (list): Names of all regional levels higher than region_level_name
    
    return: index of rows with regional variable
    
    """
    if len(higher_levels) == 1 : # only 1 weakly higher level (region level name is state)
        region_level_index = data[lower_levels].isna().all(axis="columns") 
        return region_level_index

    elif len(higher_levels) > 1 and len(lower_levels) > 1 : # regional levels is gov_district
        regional_level_mat = pd.concat([
        data[lower_levels].isna().all(axis="columns"), # municipality association and municipality are missing 
        ~data[higher_levels].isna().any(axis="columns") # state and government district are not missing
        ], axis  = "columns")  
        region_level_index = regional_level_mat.all(axis="columns")
        return region_level_index

    elif len(lower_levels) == 1: # region level is district
        regional_level_mat = pd.concat([
        data[lower_levels].isna(), # municipality are missing 
        ~data[higher_levels].isna().any(axis="columns") # state, government district and district are not missing
        ], axis  = "columns")
        region_level_index = regional_level_mat.all(axis="columns")   
        return region_level_index
    
    else:
        assert False, "Logic for regional identifier{} is unknown".format(region_level)


def save_regional_level(data, year):
    """ Finds higher regional identifiers in the Municipality dataset and saves them to mappings/csv
    Args: 
        data: municipality database
        level: regional level you want to retrieve
        year:  the current year

    """
    #if year<1993:
    #    available_regional_levels = ["state", "gov_district", "district"]
    #else:
    #    available_regional_levels = ["state", "gov_district", "district", "municipality_assoc"]
    for regional_level_name in ["state", "gov_district", "district"]:

        regional_higher_levels, regional_lower_levels = get_relative_level(data_columns = data.columns, region_level = regional_level_name)

        region_level_index = get_region_level_index(data = data, region_level = regional_level_name, lower_levels = regional_lower_levels, higher_levels = regional_higher_levels)
        
        assert len(region_level_index) > 0,  "Regional Level {} index returned empty".format(regional_level_name)
        assert region_level_index.any(), "Regional Level {} not found".format(regional_level_name)
        
        # create dataframe out of selected rows 
        region_df = pd.DataFrame(data = data.loc[region_level_index, regional_higher_levels + ["municipality_name"]].values, columns = regional_higher_levels + [regional_level_name + "_name"])
        
        # set correct data type
        region_df[regional_higher_levels] = region_df[regional_higher_levels].astype(int)
        region_df[regional_level_name + "_name"] = region_df[regional_level_name + "_name"].str.replace('"', '').astype(str)
        
        # save datafile
        region_df.to_csv(path_or_buf = DATA_MAPPINGS / "{}_{}.csv".format(regional_level_name, year), index=False)

def handle_special_cases(df, year):
    if year==2016:
        # population estimate is unreliable for this years (perhaps because of refugee inflows)
        df_fraudulent = df.loc[df["municipality_name"].str.contains("4"),:]
        df_fraudulent.to_csv(path_or_buf = DATA_MISC / "municipalities_{}_fraudulent.csv".format(year), index=False)
        df = df.drop(df_fraudulent.index, axis="index")
    elif year == 2010:
        # handle German/Luxemburg shared territory since government district is missing here (year==2015)
        region_name_columns = [column for column in df.columns if column in ("state", "gov_district", "district", "municipality_assoc", "municipality")]    
        is_missing = df[region_name_columns].isna().any(axis="columns")
        if is_missing.any(): 
            print("Dropping German/Luxemburg shared territory \n",  df.loc[is_missing, : ])
            df = df.drop(df.index[is_missing][0], axis="index")
    else:
        pass
    return df




def save_municipality_level(df, year):
    # keep only municipality codes and drop regional observations
    df = df.dropna(axis="index", how="any", subset=["state", "district", "municipality", "municipality_name"]).reset_index()


    df = handle_special_cases(df, year)
    # set correct data types

    # region types
    region_name_columns = [column for column in df.columns if column in ("state", "gov_district", "district", "municipality_assoc", "municipality")]     
    df[region_name_columns] = df[region_name_columns].astype(int)

    # geography/density columns
    geo_name_columns = [column for column in df.columns if column in ("area_km2", "pop_total", "pop_density")] 
    df[geo_name_columns] = df[geo_name_columns].astype(float)    

    # municipality name
    df["municipality_name"] = df["municipality_name"].str.replace('"', '').astype(str) 


    # save dataset
    df.to_csv(path_or_buf = DATA_MUNICIPALITIES / "municipalities_{}.csv".format(year), index=False)

