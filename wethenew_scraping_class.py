from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
import regex as re
import pandas as pd

class ScrapingWeTheNew:
    def __init__(self):
        # Initializer Chrome drivers
        self.driver = webdriver.Chrome()
        
        self.driver.delete_all_cookies()
        
        self.driver.get("https://wethenew.com/collections/all-sneakers")
        
        self.accept_cookies()
        
        # Initialize data
        self.pairs_database = {}
        
    def run(self):

        self.scrap_shoes_main_data()

        self.scrap_shoes_subdata()

        self.get_csv_from_json()
        
        return(self.pairs_database, self.pairs_database_df)

    def accept_cookies(self):
        # Accept cookies
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="didomi-notice-agree-button"]/span')
            )
        ).click()

        print("Cookies accepted")

    def scrap_shoes_main_data(self):
        nb_pages = int(self.driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div[4]/a[4]').text)

        for i in range(1):
            print(f"Loading data from page {i+1}")
            
            self.driver.get(f"https://wethenew.com/collections/all-sneakers?page={i+1}")
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            # Search elements from 'styles_card__GmAAu styles_ProductCard__q4Ys8' class which correspond to a shoes item in frontend
            elements = soup.find_all("div", class_="styles_card__GmAAu styles_ProductCard__q4Ys8")

            # price and name are located in a <a> & <p> tags
            for element in elements:
                a_el = element.find("a")
                
                href = a_el["href"]
                
                pair_name = a_el.text.strip()

                price_el = element.find("p").text.strip()
                
                price = re.findall("(\d+)€",price_el)[0]
                
                self.pairs_database[pair_name] = {}
                self.pairs_database[pair_name]["price"] = price
                self.pairs_database[pair_name]["href"] = href
                self.pairs_database[pair_name]["sizes"] = {}

    def scrap_shoes_subdata(self):
        
        for pair in self.pairs_database:
            
            href = self.pairs_database[pair]["href"]
            
            self.driver.get(f"https://wethenew.com{href}")

            # We the widget about sizes
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="__next"]/div/main/div[1]/div[2]/div[3]/button/span')
                )
            ).click()
            
            el_ = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'styles_SizeGrid__IXQ0b')
                )
            )
            
            # Extract html content & soup from this specific shoes to get sizes
            html_content = el_.get_attribute("outerHTML")

            soup_element = BeautifulSoup(html_content, "html.parser")
            
            buttons = soup_element.find_all("button")

            # All sizes are located on buttons
            for button in buttons:
                btn_elements = button.find_all("p")
                
                size, price = btn_elements[0].text.strip(' EU'), btn_elements[1].text.strip('€')
                
                self.pairs_database[pair]["sizes"][size] = price
            break
                
    def get_csv_from_json(self):
        
        # Transformer les dictionnaires en DataFrame
        df = pd.DataFrame(self.pairs_database)

        self.pairs_database_df = df
        