import os
import requests
import json
import csv
import psycopg2
from bs4 import BeautifulSoup



base_url = 'https://www.skinwallet.com/en/market/get-offers?appId=730&page='
file_path = r"response.csv"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"



headers = {
    "User-Agent": user_agent
}


 
if os.path.exists(file_path):
    os.remove(file_path)
    print("'response.csv' removed successfully")



for page in range(1, 416):
    url = base_url + str(page)
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        extracted_data = []
        for offer in data['offerThumbnails']['thumbnails']:
            extracted_data.append({
                'marketHashName': offer['marketHashName'],
                'price': {
                            'amount': offer['price'] ['amount']          },
                'url': f"https://www.skinwallet.com/market/offer/{offer['offerId']}"
            })

        with open(file_path, 'a', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['marketHashName', 'price', 'url'])
            
            if page == 1:
                writer.writeheader()
            
            for item in extracted_data:
                item['price'] = item['price']['amount']
                writer.writerow(item)

        print(f'Страница {page} сохранена в файле response.csv,"SKINWALLET"')
    else:
        print(f'Ошибка при выполнении запроса на странице {page}:', response.status_code)


    conn = psycopg2.connect(
        user="postgres",
        password="1090",
        host="localhost",
        database="projects",
        port="5432",
        client_encoding="utf-8"
    )
cursor = conn.cursor()



delete_table_query = '''
    DROP TABLE if EXISTS skinwallet 
'''
cursor.execute(delete_table_query)
print('Table "SKINWALLET" deleted')



create_table_query = '''
    CREATE TABLE if not EXISTS  skinwallet (
        name varchar(250),
        price varchar(250),
        iznos varchar(250),
        item_page varchar(250)
    )
'''
cursor.execute(create_table_query)



with open(file_path, 'r', newline='', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        insert_query = '''
            INSERT INTO skinwallet (name, price, item_page)
            VALUES (%s, %s, %s)
        '''
        price = float(row['price']) / 100
        cursor.execute(insert_query, (row['marketHashName'], price, row['url']))

conn.commit()
print('Data imported successfully,"SKINWALLET"')



add_column_query = '''
ALTER TABLE skinwallet
ADD COLUMN type VARCHAR(250)
'''
cursor.execute(add_column_query)
conn.commit()
print("Column 'type' added successfully,'SKINWALLET'")



update_type_query = '''
UPDATE skinwallet
SET type =
    CASE
        WHEN name LIKE '%Glock-18%' OR name LIKE '%P2000%' OR name LIKE '%USP-S%' OR name LIKE '%Dual Berettas%' OR name LIKE '%P250%' OR name LIKE '%Tec-9%' OR name LIKE '%Five-SeveN%' OR name LIKE '%CZ75-Auto%' OR name LIKE '%Desert Eagle%' OR name LIKE '%R8 Revolver%' THEN 'Pistols'
        WHEN name LIKE '%MAC-10%' OR name LIKE '%MP9%' OR name LIKE '%MP7%' OR name LIKE '%MP5-SD%' OR name LIKE '%UMP-45%' OR name LIKE '%P90%' OR name LIKE '%PP-Bizon%' THEN 'SMG'
        WHEN name LIKE '%Galil AR%' OR name LIKE '%FAMAS%' OR name LIKE '%AK-47%' OR name LIKE '%M4A4%' OR name LIKE '%M4A1-S%' OR name LIKE '%AUG%' OR name LIKE '%SG 553%' OR name LIKE '%SSG 08%' OR name LIKE '%AWP%' OR name LIKE '%G3SG1%' OR name LIKE '%SCAR-20%' THEN 'Rifle'
        WHEN name LIKE '%Nova%' OR name LIKE '%XM1014%' OR name LIKE '%Sawed-Off%' OR name LIKE '%MAG-7%' OR name LIKE '%M249%' THEN 'Heavy'
        WHEN name LIKE '%Knife%' OR name LIKE '%Tactical Knife%' OR name LIKE '%Karambit%' OR name LIKE '%Butterfly Knife%' OR name LIKE '%Machete%' OR name LIKE '%Navaja%' OR name LIKE '%Flip Knife%' OR name LIKE '%Gut Knife%' OR name LIKE '%Bayonet%' OR name LIKE '%M9 Bayonet%' OR name LIKE '%Huntsman Knife%' OR name LIKE '%Falchion Knife%' OR name LIKE '%Butterfly Knife%' OR name LIKE '%Shadow Daggers%' OR name LIKE '%Ursus Knife%' OR name LIKE '%Navaja Knife%' THEN 'Knife'
        WHEN name LIKE '%Sport Gloves%' OR name LIKE '%Moto Gloves%' OR name LIKE '%Hand Wraps%' OR name LIKE '%Driver Gloves%' OR name LIKE '%Specialist Gloves%' OR name LIKE '%Bloodhound Gloves%' OR name LIKE '%Hydra Gloves%' OR name LIKE '%Broken Fang Gloves%' THEN 'gloves'
        ELSE 'none'
    END;
'''
cursor.execute(update_type_query)
conn.commit()
print("Column 'type' updated successfully,'SKINWALLET'")



update_price_column_query = '''
UPDATE skinwallet
SET price = REPLACE(price, ' ', '');
'''
cursor.execute(update_price_column_query)
conn.commit()
print("Column 'price' updated successfully,'SKINWALLET'")



update_price_type_query = '''
ALTER TABLE skinwallet
ALTER COLUMN price TYPE DECIMAL(10,2) USING price::numeric(10,2);
'''
cursor.execute(update_price_type_query)
conn.commit()
print("Column 'price' updated successfully.'SKINWALLET'")



delete_non_type_query = '''
DELETE FROM skinwallet
WHERE type = 'none';
'''
cursor.execute(delete_non_type_query)
conn.commit()



delete_repetition_data_query='''
DELETE FROM skinwallet
WHERE (price) NOT IN (
    SELECT MIN(price)
    FROM skinwallet
    GROUP BY name
);
'''
cursor.execute(delete_repetition_data_query)
conn.commit()
print("Useless data deleted,'SKINWALLET'")



update_query = '''
UPDATE skinwallet
SET iznos =
    CASE
        WHEN name LIKE '%(Battle-Scarred)%' THEN 'Battle-Scarred'
        WHEN name LIKE '%(Factory New)%' THEN 'Factory New'
        WHEN name LIKE '%(Field-Tested)%' THEN 'Field-Tested'
        WHEN name LIKE '%(Minimal Wear)%' THEN 'Minimal Wear'
        WHEN name LIKE '%(Well-Worn)%' THEN 'Well-Worn'
        ELSE ''
    END;
'''
cursor.execute(update_query)
conn.commit()
print("Column 'iznos' updated successfully,'SKINWALLET'")



update_column_name_query1 = '''
UPDATE skinwallet
SET name =
    REPLACE(
        REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(name, '(Battle-Scarred)', ''),
                    '(Factory New)', ''
                ),
                '(Field-Tested)', ''
            ),
            '(Minimal Wear)', ''
        ),
        '(Well-Worn)', ''
    )
WHERE name LIKE '%(Battle-Scarred)%'
    OR name LIKE '%(Factory New)%'
    OR name LIKE '%(Field-Tested)%'
    OR name LIKE '%(Minimal Wear)%'
    OR name LIKE '%(Well-Worn)%';
'''
cursor.execute(update_column_name_query1)
conn.commit()
print("Column 'name' updated successfully,'SKINWALLET'")



print("Script execution completed,'SKINWALLET'")




def save_response_to_csv(response, filename, fields):
    with open(filename, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        for row in response:
            filtered_row = {key: row[key] for key in fields}
            writer.writerow(filtered_row)
    print(f"Ответ сохранен в файле: {filename}")

url = "https://api.skinport.com/v1/items"
params = {
    "app_id": 730,
    "currency": "RUB",
    "tradable": 0
}



response = requests.get(url, params=params).json()
filename = r"skinport.csv"
selected_fields = ["market_hash_name", "mean_price", "item_page"]
save_response_to_csv(response, filename, selected_fields)
conn.autocommit = True



drop_table_query = "drop table if exists skinport;"
cursor = conn.cursor()
cursor.execute(drop_table_query)
print("Table 'SKINPORT' deleted successfully.")



create_table_query = '''
    CREATE TABLE if not EXISTS SKINPORT (
        name VARCHAR(250),
        price VARCHAR(250),
        item_page VARCHAR(250),
        iznos VARCHAR(250)
    )
'''
cursor.execute(create_table_query)
conn.commit()
print("Table 'SKINPORT' created successfully.")



with open(r'skinport.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
        if i == 0:
            continue
        cursor.execute("INSERT INTO SKINPORT (name, price, item_page) VALUES (%s, %s, %s);", row)
print("Data loaded into 'SKINPORT' table successfully.")



add_column_query = '''
alter table SKINPORT
add column type varchar(250)
'''
cursor.execute(add_column_query)
conn.commit()
print("Column 'type' added successfully,'SKINPORT'")



update_type_query = '''
UPDATE skinport
SET type =
    CASE
        WHEN name LIKE '%Glock-18%' OR name LIKE '%P2000%' OR name LIKE '%USP-S%' OR name LIKE '%Dual Berettas%' OR name LIKE '%P250%' OR name LIKE '%Tec-9%' OR name LIKE '%Five-SeveN%' OR name LIKE '%CZ75-Auto%' OR name LIKE '%Desert Eagle%' OR name LIKE '%R8 Revolver%' THEN 'Pistols'
        WHEN name LIKE '%MAC-10%' OR name LIKE '%MP9%' OR name LIKE '%MP7%' OR name LIKE '%MP5-SD%' OR name LIKE '%UMP-45%' OR name LIKE '%P90%' OR name LIKE '%PP-Bizon%' THEN 'SMG'
        WHEN name LIKE '%Galil AR%' OR name LIKE '%FAMAS%' OR name LIKE '%AK-47%' OR name LIKE '%M4A4%' OR name LIKE '%M4A1-S%' OR name LIKE '%AUG%' OR name LIKE '%SG 553%' OR name LIKE '%SSG 08%' OR name LIKE '%AWP%' OR name LIKE '%G3SG1%' OR name LIKE '%SCAR-20%' THEN 'Rifle'
        WHEN name LIKE '%Nova%' OR name LIKE '%XM1014%' OR name LIKE '%Sawed-Off%' OR name LIKE '%MAG-7%' OR name LIKE '%M249%' THEN 'Heavy'
        WHEN name LIKE '%Knife%' OR name LIKE '%Tactical Knife%' OR name LIKE '%Karambit%' OR name LIKE '%Butterfly Knife%' OR name LIKE '%Machete%' OR name LIKE '%Navaja%' OR name LIKE '%Flip Knife%' OR name LIKE '%Gut Knife%' OR name LIKE '%Bayonet%' OR name LIKE '%M9 Bayonet%' OR name LIKE '%Huntsman Knife%' OR name LIKE '%Falchion Knife%' OR name LIKE '%Butterfly Knife%' OR name LIKE '%Shadow Daggers%' OR name LIKE '%Ursus Knife%' OR name LIKE '%Navaja Knife%' THEN 'Knife'
        WHEN name LIKE '%Sport Gloves%' OR name LIKE '%Moto Gloves%' OR name LIKE '%Hand Wraps%' OR name LIKE '%Driver Gloves%' OR name LIKE '%Specialist Gloves%' OR name LIKE '%Bloodhound Gloves%' OR name LIKE '%Hydra Gloves%' OR name LIKE '%Broken Fang Gloves%' THEN 'gloves'
    ELSE 'none'
END;
'''
cursor.execute(update_type_query)
conn.commit()
print("Column 'type' updated successfully,'SKINPORT'")



update_query = '''
UPDATE skinport
SET iznos =
    CASE
        WHEN name LIKE '%(Battle-Scarred)%' THEN 'Battle-Scarred'
        WHEN name LIKE '%(Factory New)%' THEN 'Factory New'
        WHEN name LIKE '%(Field-Tested)%' THEN 'Field-Tested'
        WHEN name LIKE '%(Minimal Wear)%' THEN 'Minimal Wear'
        WHEN name LIKE '%(Well-Worn)%' THEN 'Well-Worn'
        ELSE ''
    END;
'''
cursor.execute(update_query)
conn.commit()
print("Column 'iznos' updated successfully,'SKINPORT'")




update_column_name_query1 = '''
UPDATE skinport
SET name =
    REPLACE(
        REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(name, '(Battle-Scarred)', ''),
                    '(Factory New)', ''
                ),
                '(Field-Tested)', ''
            ),
            '(Minimal Wear)', ''
        ),
        '(Well-Worn)', ''
    )
WHERE name LIKE '%(Battle-Scarred)%'
    OR name LIKE '%(Factory New)%'
    OR name LIKE '%(Field-Tested)%'
    OR name LIKE '%(Minimal Wear)%'
    OR name LIKE '%(Well-Worn)%';
'''
cursor.execute(update_column_name_query1)
conn.commit()
print("Column 'name' updated successfully,'SKINPORT'")



trim_column_price_query = '''
UPDATE skinport
SET price = TRIM(price)
'''
cursor.execute(trim_column_price_query)
conn.commit()
print("Column 'price' trimmed successfully,'SKINPORT'")



delete_non_type_query = '''
DELETE FROM skinport
WHERE type = 'none';
'''
cursor.execute(delete_non_type_query)
conn.commit()



delete_repetition_data_query='''
DELETE FROM skinport
WHERE (price) NOT IN (
    SELECT MIN(price)
    FROM skinport
    GROUP BY name
);
'''
cursor.execute(delete_repetition_data_query)
conn.commit()
print("Useless data deleted,'SKINPORT'")























conn = psycopg2.connect(
    user="postgres",
    password="1090",
    host="localhost",
    database="projects",
    port="5432",
    client_encoding="utf-8"
)
conn.autocommit = True
cursor = conn.cursor()



terminate_connections_query = '''
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = 'projects1'
      AND pid <> pg_backend_pid();
'''
cursor.execute(terminate_connections_query)
conn.commit()



delete_table_query = "DROP TABLE IF EXISTS lisskins;"
cursor.execute(delete_table_query)
print("TABLE 'LISSKINS' deleted successfully.")



def parse_document(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    items = soup.find_all('div', class_='item')
    parsed_data = []
    for item in items:
        name_element = item.find('div', class_='name-inner')
        name = name_element.text.strip()

        price_element = item.find('div', class_='price')
        price = price_element.text.strip()

        exterior_element = item.find('div', class_='name-exterior')
        exterior = exterior_element.text.strip() if exterior_element else ''

        link_element = item.find('a', class_='name')
        link = link_element['href']

        parsed_data.append((name, price, exterior, link))

    return parsed_data



base_url = 'https://lis-skins.ru/market/csgo/?page='
start_page = 1
num_items_per_page = 60
max_iterations = 119



for i in range(max_iterations):
    url = base_url + str(start_page + i)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open('response.html', 'w', encoding='utf-8') as file:
            file.write(response.text)
        print('Result successfully saved to response.html.')

        with open('response.html', 'r', encoding='utf-8') as file:
            html_content = file.read()

        result = parse_document(html_content)
        processed_result = []
        for name, price, exterior, link in result:
            processed_data = (name, price, exterior, link)
            processed_result.append(processed_data)

        with open('lisskins.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for processed_data in processed_result:
                writer.writerow(processed_data)

        print(f"Iteration {i+1} - Result written to lisskins.csv file.")
    else:
        print('An error occurred while making the request.')




print("Parsing complete. 'LISSKINS'")



conn = psycopg2.connect(
    user="postgres",
    password="1090",
    host="localhost",
    database="projects",
    port="5432",
    client_encoding="utf-8"
)
conn.autocommit = True



drop_table_query = '''
    drop table if exists lisskins;
'''
cursor.execute(drop_table_query)
conn.commit()
print("Table 'LISSKINS' deleted successfully.")



create_table_query = '''
    CREATE TABLE if not EXISTS lisskins (
        name VARCHAR(250),
        price VARCHAR(250),
        iznos VARCHAR(250),
        item_page VARCHAR(250)
    )
'''
cursor.execute(create_table_query)
conn.commit()
print("Table 'LISSKINS' created successfully.")



with open('lisskins.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
        if i == 0:
            continue
        cursor.execute("INSERT INTO lisskins (name, price, iznos, item_page) VALUES (%s, %s, %s, %s);", row)
print("Data loaded into 'LISSKINS' table successfully.")



add_column_query = '''
    ALTER TABLE lisskins
    ADD COLUMN type VARCHAR(250)
'''
cursor.execute(add_column_query)
conn.commit()
print("Column 'type' added successfully,'LISSKINS'")



update_type_query = '''
    UPDATE lisskins
    SET type =
        CASE
            WHEN name LIKE '%Glock-18%' OR name LIKE '%P2000%' OR name LIKE '%USP-S%' OR name LIKE '%Dual Berettas%' OR name LIKE '%P250%' OR name LIKE '%Tec-9%' OR name LIKE '%Five-SeveN%' OR name LIKE '%CZ75-Auto%' OR name LIKE '%Desert Eagle%' OR name LIKE '%R8 Revolver%' THEN 'Pistols'
            WHEN name LIKE '%MAC-10%' OR name LIKE '%MP9%' OR name LIKE '%MP7%' OR name LIKE '%MP5-SD%' OR name LIKE '%UMP-45%' OR name LIKE '%P90%' OR name LIKE '%PP-Bizon%' THEN 'SMG'
            WHEN name LIKE '%Galil AR%' OR name LIKE '%FAMAS%' OR name LIKE '%AK-47%' OR name LIKE '%M4A4%' OR name LIKE '%M4A1-S%' OR name LIKE '%AUG%' OR name LIKE '%SG 553%' OR name LIKE '%SSG 08%' OR name LIKE '%AWP%' OR name LIKE '%G3SG1%' OR name LIKE '%SCAR-20%' THEN 'Rifle'
            WHEN name LIKE '%Nova%' OR name LIKE '%XM1014%' OR name LIKE '%Sawed-Off%' OR name LIKE '%MAG-7%' OR name LIKE '%M249%' THEN 'Heavy'
            WHEN name LIKE '%Knife%' OR name LIKE '%Tactical Knife%' OR name LIKE '%Karambit%' OR name LIKE '%Butterfly Knife%' OR name LIKE '%Machete%' OR name LIKE '%Navaja%' OR name LIKE '%Flip Knife%' OR name LIKE '%Gut Knife%' OR name LIKE '%Bayonet%' OR name LIKE '%M9 Bayonet%' OR name LIKE '%Huntsman Knife%' OR name LIKE '%Falchion Knife%' OR name LIKE '%Butterfly Knife%' OR name LIKE '%Shadow Daggers%' OR name LIKE '%Ursus Knife%' OR name LIKE '%Navaja Knife%' THEN 'Knife'
            WHEN name LIKE '%Sport Gloves%' OR name LIKE '%Moto Gloves%' OR name LIKE '%Hand Wraps%' OR name LIKE '%Driver Gloves%' OR name LIKE '%Specialist Gloves%' OR name LIKE '%Bloodhound Gloves%' OR name LIKE '%Hydra Gloves%' OR name LIKE '%Broken Fang Gloves%' THEN 'Gloves'
        ELSE 'none'
    END;
'''
cursor.execute(update_type_query)
conn.commit()
print("Column 'type' updated successfully,'LISSKINS'")



trim_column_price_query = '''
UPDATE lisskins
SET price = REPLACE(price, ' ', '')
'''
cursor.execute(trim_column_price_query)
conn.commit()
print("Spaces removed from the 'price' column successfully,'LISSKINS'")



left_column_iznos_query = '''
UPDATE lisskins
SET iznos = REPLACE(iznos, '(', '')
'''
cursor.execute(left_column_iznos_query)
conn.commit()



righgt_column_iznos_query = '''
UPDATE lisskins
SET iznos = REPLACE(iznos, ')', '')
'''
cursor.execute(righgt_column_iznos_query)
conn.commit()
print("'()'removed from the 'iznos' column successfully,'LISSKINS'")



update_price_type_query = '''
ALTER TABLE lisskins
ALTER COLUMN price TYPE DECIMAL(10,2) USING price::numeric(10,2);
'''
cursor.execute(update_price_type_query)
conn.commit()
print("Column 'price' updated successfully,'LISSKINS'")



delete_non_type_query = '''
DELETE FROM lisskins
WHERE type = 'none';
'''
cursor.execute(delete_non_type_query)
conn.commit()
print("Usles data deleted from 'LISSKINS'")



update_non_iznos_query = '''
UPDATE lisskins
SET iznos = 'Factory New'
WHERE type = 'Knife' AND iznos IS NULL;
'''
cursor.execute(update_non_iznos_query)
conn.commit()
print("Column 'iznos' updated successfully, 'LISSKINS'")



cursor.close()
conn.close()
print("Parsing complete.")