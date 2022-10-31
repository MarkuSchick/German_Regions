""" Requests helper to automatically download excel files from destatis """
import requests

from config import DATA_RAW


def download_from_destatis(year):
    url = "https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/Administrativ/Archiv/GVAuszugJ/3112{}_Auszug_GV.xlsx?__blob=publicationFile".format(year)

    # Load excel files
    resp = requests.get(url)
    return resp


def save_request_to_excel(response,out_filename):
    """ Saves an request response as an excel file
    Args:
        response: request.response
        out_filename: name of saved excel
    """
    output = open(DATA_RAW / '{}.xls'.format(out_filename), 'wb')
    output.write(response.content)
    output.close()
