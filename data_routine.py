from bs4 import BeautifulSoup
import os
import requests


def download_file_aod(url,path):
    full_filename = url.split('/')[-1]
    local_filename = full_filename.split('.')[1]+'.nc'
    r = requests.get(url, stream=True)
    local_path_file = path+local_filename
    if not os.path.isfile(local_path_file):
        with open(path+local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return local_filename
    else:
        print "Is exsist "+url


def download_aod():
    from_year = 2004
    to_year = 2018

    list_year = range(from_year, to_year)
    page = "https://ladsweb.modaps.eosdis.nasa.gov/opendap/allData/61/MYD08_D3/<year>/contents.html"
    dataset = ".nc4?AOD_550_Dark_Target_Deep_Blue_Combined_Mean[0:1:179][0:1:359]"
    for year in list_year:
        page_year = page.replace("<year>",str(year))
        r = requests.get(page_year)
        str_page_year = r.text
        soup_year = BeautifulSoup(str_page_year, features="lxml")
        for link in soup_year.find_all('a'):
            ref = link.get('href')
            if 'contents.html' in ref:
                filename_page = page_year.replace('contents.html',ref)
                filename_r = requests.get(filename_page).text
                filename_soup = BeautifulSoup(filename_r, features="lxml")
                for link_page in filename_soup.find_all('a'):
                    file_name = link_page.get('href')
                    if '.hdf.info' in file_name:
                        link_file = filename_page.replace('contents.html', file_name).replace('.info','')
                        print 'downloading ' + link_file
                        download_file_aod(link_file+dataset,'/Users/maritim/Project/MY_PROJECT/JOHN/data/raw/')


if __name__ == '__main__':
    download_aod()