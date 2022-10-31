""" prepares raw data from destatis """
from data_analysis import aggregate_district_data
from download_helper import download_from_destatis, save_request_to_excel
from identify_regional_helper import load_excel_data, save_regional_level, save_municipality_level


def prepare_wave(year):
    """ download raw data from destatis, 
        stores regional levels and municipalities
        in separate data folders
    Args:
        year: year of desired wave
    """
    print(year)
    # request = download_from_destatis(year)
    
    # save_request_to_excel(request, "municipalities{}".format(year))
    
    df = load_excel_data(year)

    save_regional_level(df, year)

    save_municipality_level(df, year)



if __name__ == "__main__":
    for year in range(1985, 2020, 1):
        prepare_wave(year)

    for year in range(1985, 2020, 1):
        aggregate_district_data(year)
    

