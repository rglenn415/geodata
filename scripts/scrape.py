import csv
from bs4 import BeautifulSoup

def extract_table_details(html):
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.select(".forge-table-body__row")
    
    data = []
    for row in rows:
        cells = row.select(".forge-table-body__cell")
        if len(cells) >= 4:
            column_name = cells[0].select_one("span").text.strip()
            description = cells[1].select_one(".collapsed-text-section div").text.strip()
            api_field_name = cells[2].select_one("span").text.strip()
            data_type = cells[3].select_one("a").text.strip()
            
            data.append({
                "Column Name": column_name,
                "Description": description,
                "API Field Name": api_field_name,
                "Data Type": data_type
            })
    
    return data

# Example usage:
if __name__ == "__main__":
    with open("scraped.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    
    table_data = extract_table_details(html_content)
    
    # Writing to CSV file
    keys = table_data[0].keys()
  
    with open('output.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(table_data)