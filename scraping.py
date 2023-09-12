from bs4 import BeautifulSoup
import requests
import pandas as pd
import math
from db_connection import *
from selenium import webdriver

lista_carti = []
x = 30

def scrap_anticariatunu():
    #stabilirea url-ului si finisarea datelor
    anticariat_unu = "https://www.anticariat-unu.ro/carti-pentru-copii-literatura-populara-benzi-desenate-c45"
    r_unu = requests.get(anticariat_unu)
    soup_unu = BeautifulSoup(r_unu.content, 'lxml')
    total_pagini = soup_unu.find(class_='last').find('a',href=True)['href']
    z = total_pagini.split("/")[4]
    # for pentru a da scrap la fiecare pagina
    for i in range(0, int(z)+1, x):
        url_unu = f"https://www.anticariat-unu.ro/carti-pentru-copii-literatura-populara-benzi-desenate-c45/{i}"
        response = requests.get(url_unu)
        response = response.content

        soup = BeautifulSoup(response, 'lxml')
        carti = soup.find_all(class_='col-6 col-md-4 col-lg-3 mb-5')

        #for pentru a lua fiecare carte de pe fiecare pagina
        for carte in carti:
            carte_titlu = carte.find('h3').find('a').string
            carte_titlu = carte_titlu[34:len(carte_titlu)]
            carte_titlu = carte_titlu[:-28]
            carte_pret = carte.find(class_='price').text.replace(' ', '').replace('\n', ' ')
            carte_pret = float(carte_pret[:-4])
            carte_link = carte.find('h3').find('a').get('href')
            query = "INSERT INTO carte (Nume, Pret, CarteLink) VALUES (?, ?, ?)"
            values = (carte_titlu, carte_pret, carte_link)
            cursor.execute(query, values)
            connection.commit()



def scrap_targulcartii():
    targul_cartii="https://www.targulcartii.ro/altele/benzi-desenate"
    r_targul_cartii = requests.get(targul_cartii)
    soup_targul_cartii = BeautifulSoup(r_targul_cartii.content, 'lxml')
    tot_pagini_tc = soup_targul_cartii.find(class_="pagination_total_pages").text


    for i in range(1, int(tot_pagini_tc)+1, 1):
        urltarg = f"https://www.targulcartii.ro/altele/benzi-desenate?page={i}"
        response = requests.get(urltarg)
        targcarti = response.content

        soup = BeautifulSoup(targcarti, 'lxml')
        carti = soup.find_all(class_='product list')

        for carte in carti:
            carte_titlu = carte.find(class_='name').text
            carte_pret = carte.find(class_='price_value').text
            if carte_pret == '':
                carte_pret = carte.find(class_='price-new').text
            carte_pret = float(carte_pret[43:-31].replace(',', '.'))
            carte_link = carte.find('div', class_='name').find('a').get('href')
            print(carte_link)

            query = "INSERT INTO carte (Nume, Pret, CarteLink) VALUES (?, ?, ?)"
            values = (carte_titlu, carte_pret, carte_link)
            cursor.execute(query, values)
            connection.commit()



def scrap_okian():
    url_okian = "https://okian.ro/books/fiction-related-items/graphic-novels/graphic-novels-manga.html?p=1"
    r_url_okian = requests.get(url_okian)
    soup_url_okian = BeautifulSoup(r_url_okian.content, 'lxml')
    nr_carti_okian = soup_url_okian.find(class_='category_sort sides').find(class_='left').text[6:-5].split()[3]
    nr_pagini_okian = math.ceil(int(nr_carti_okian)/24)

    for i in range(1,nr_pagini_okian+1):
        url = f"https://okian.ro/books/fiction-related-items/graphic-novels/graphic-novels-manga.html?p={i}"
        r = requests.get(url)
        r = r.content
        soup = BeautifulSoup(r, 'lxml')
        carti = soup.find_all(class_='single_prd')

        for carte in carti:
            carte_titlu = carte.find('h3').text
            carte_pret = (carte.find(class_='theprice new_price').text)
            carte_pret = float(carte_pret[:-4])
            carte_link = carte.find('div', class_='product_contains').find('a').get('href')
            query = "INSERT INTO carte (Nume, Pret, CarteLink) VALUES (?, ?, ?)"
            values = (carte_titlu, carte_pret, carte_link)
            cursor.execute(query, values)
            connection.commit()


def scrap_carturesti():
    driver = webdriver.Chrome()
    driver.get("https://carturesti.ro/raft/manga-2431")
    nr_pagini_carturesti = driver.find_element("xpath", '//*[@id="coloana-produse"]/product-grid-pagination[1]/div/div[1]/div/product-grid-counter/div/span')
    print(nr_pagini_carturesti)


def scrap_siteuri():
    print("Scrapingul a inceput")
    scrap_targulcartii()
    print("Scrap Targul Cartii")
    scrap_okian()
    print("Scrap Okian")
    scrap_anticariatunu()
    print("Scrap Anticariat Unu")
    print("Scrapingul s-a finalizat")

