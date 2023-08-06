from wethenew_scraping_class import ScrapingWeTheNew
import json

if __name__ == "__main__":
    
    data_json, data_df  = ScrapingWeTheNew().run()

    # Exporter le df en .csv
    data_df.to_csv("data/result.csv")
    
    # Exporter le dictionnaire en .json
    with open("data/result.json", "w") as json_file:
        json.dump(data_json, json_file)