from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import sqlite3
import hashlib

##
# Создание Flask-приложения
app = Flask(__name__)
# Подключение к базе данных

def initialize_database():
    conn = sqlite3.connect('myapp.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Устанавливаем row_factory для доступа по именам колонок
    cursor = conn.cursor()

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY, username TEXT, email TEXT UNIQUE, password TEXT)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS products
                  (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, discount REAL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS carts
                  (id INTEGER PRIMARY KEY, user_id INTEGER, total_price REAL, total_discount REAL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS cart_items
                  (id INTEGER PRIMARY KEY, cart_id INTEGER, product_id INTEGER, quantity INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS drugs_categories
                  (category_id SERIAL PRIMARY KEY, category_name TEXT NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS drugs_categories
                          (category_id SERIAL PRIMARY KEY, category_name TEXT NOT NULL)''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS calculation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calculation_id INTEGER,  
            user_id INTEGER NOT NULL,
            drug_id INTEGER NOT NULL,
            drug_name TEXT,
            username TEXT,
            weight REAL NOT NULL,
            dosage_mls REAL,
            dosage_mgs REAL,
            totalMgs REAL,
            totalhigh REAL,
            totalhighsachets REAL,
            maximumMgsPerDay REAL,
            highMgs REAL,
            loading_dose INTEGER,
            strep_drug INTEGER,
            messageMgs TEXT,
            messageOther TEXT,
            calculation_type TEXT,
            calculation_status TEXT,
            calculation_version TEXT,
            patient_id INTEGER,
            patient_name TEXT,
            error_message TEXT,
            calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            age REAL)''')

        # drugs_categories = [
        #     (1, 'Analgesics'),
        #     (2, 'Antibiotics'),
        #     (3, 'Anti-inflammatory'),
        #     (4, 'Antipyretic'),
        #     (5, 'Antiviral')
        # ]
        # cursor.executemany("INSERT INTO drugs_categories (category_id, category_name) VALUES (?, ?)", drugs_categories)

# Новая таблица для препаратов
        cursor.execute('''CREATE TABLE IF NOT EXISTS drugs
                (id INTEGER PRIMARY KEY,
                 category_id SERIAL,
                 name TEXT UNIQUE,
                 tablet_only INTEGER,
                 mls_var REAL,
                 mgs_var REAL,
                 number_of_times_a_day TEXT,
                 mls_max REAL,
                 mgs_max REAL,
                 loading_dose INTEGER,
                 mls_var_loading REAL,
                 mgs_var_loading REAL,
                 mls_max_loading REAL,
                 mgs_max_loading REAL,
                 instructions TEXT,
                 nzf_link TEXT,
                 high_range INTEGER,
                 high_modifier REAL,
                 mls_max_high REAL,
                 mgs_max_high REAL,
                 strep_drug INTEGER,
                 strep_frequency TEXT,
                 mls_var_strep REAL,
                 mgs_var_strep REAL,
                 mls_strep_max REAL,
                 mgs_strep_max REAL,
                 weight_cutoff_1 REAL,
                 weight_cutoff_2 REAL,
                 range1_dose REAL,
                 range2_dose REAL,
                 form TEXT,
                 age_range REAL
                 )''')

# Заполнение данных препаратов (пример для нескольких записей)
        drugs_data = [
            ('Paracetamol120', 1, False, 0.625, 15, 'every four hours, up to a maximum of four doses in 24 hours', 42,
             1000, True, 1.25, 30, 62.5, 1500,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15 mg/kg per dose (maximum 1 g) every four hours; maximum 75 mg/kg per day (without exceeding 4 g) for 48 hours, maximum of 60 mg/kg per day (without exceeding 4 g) thereafter <br> <span class=\'age-group\'> Note</span> A loading dose of 30 mg/kg (maximum 1.5 g) may be given provided there has been no paracetamol given within the preceding 12 hours</div></div>',
             'https://nzfchildren.org.nz/nzf_2439', False, None, None, None, False, '', None, None, None, None, None, None, None, None, None, None),
            ('Paracetamol250', 1, False, 0.3, 15, 'every four hours, up to a maximum of four doses in 24 hours', 20,
             1000, True, 0.6, 30, 30, 1500,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15 mg/kg per dose (maximum 1 g) every four hours; maximum 75 mg/kg per day (without exceeding 4 g) for 48 hours, maximum of 60 mg/kg per day (without exceeding 4 g) thereafter <br> <span class=\'age-group\'> Note</span> A loading dose of 30 mg/kg (maximum 1.5 g) may be given provided there has been no paracetamol given within the preceding 12 hours</div></div>',
             'https://nzfchildren.org.nz/nzf_2439', False, None, None, None, False, '', None, None, None, None, None, None, None, None, None, None),
            ('Paracetamol120nonloading', 1, False, 0.625, 15,
             'every four hours, up to a maximum of four doses in 24 hours', 42, 1000, False, 1.25, 30, 62.5, 1500,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15 mg/kg per dose (maximum 1 g) every four hours; maximum 75 mg/kg per day (without exceeding 4 g) for 48 hours, maximum of 60 mg/kg per day (without exceeding 4 g) thereafter</div></div>',
             'https://nzfchildren.org.nz/nzf_2439', False, None, None, None, False, '', None, None, None, None, None, None, None, None, None, None),
            ('Paracetamol250nonloading', 1, False, 0.3, 15,
             'every four hours, up to a maximum of four doses in 24 hours', 20, 1000, False, 0.6, 30, 30, 1500,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15 mg/kg per dose (maximum 1 g) every four hours; maximum 75 mg/kg per day (without exceeding 4 g) for 48 hours, maximum of 60 mg/kg per day (without exceeding 4 g) thereafter</div></div>',
             'https://nzfchildren.org.nz/nzf_2439', False, None, None, None, False, '', None, None, None, None, None, None, None, None, None, None),
            ('Ibuprofen100', 1, False, 0.25, 5, 'three to four times a day', 10, 200, False, None, None, None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 - 3 months</span> 5 mg/kg 3-4 times daily <br> <span class=\'age-group\'> 3 months - 18 years</span> 5-10 mg/kg 3 or 4 times daily up to 30 mg/kg daily (maximum 2.4 g daily)</div></div>',
             'https://nzfchildren.org.nz/nzf_5524', True, 2, 20, 400, False, '', None, None, None, None, None, None, None, None, None, None),
            ('Ibuprofen100norange', 1, False, 0.3, 6, 'three times a day', 20, 400, False, None, None, None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>3 months - 18 years</span> 6 mg/kg per dose (maximum 400mg) every 8 hours as needed for pain or fever. Do not take more than 3 doses in 24 hours.</div></div>',
             'https://nzfchildren.org.nz/nzf_5524', False, 2, 20, 400, False, '', None, None, None, None, None, None, None, None, None, None),
            ('Ibuprofen200norange', 1, False, 0.15, 6, 'three times a day', 10, 400, False, None, None, None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>3 months - 18 years</span> 6 mg/kg per dose (maximum 400mg) every 8 hours as needed for pain or fever. Do not take more than 3 doses in 24 hours.</div></div>',
             'https://nzfchildren.org.nz/nzf_5524', False, 2, 10, 400, False, '', None, None, None, None, None, None, None, None, None, None),
            ('Amoxicillin125', 2, False, 0.6, 15, 'three times a day', 40, 1000, False, None, None, None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15 - 30mg/kg (maximum 1,000mg) three times daily </div> <strong>Strep A Dosing:</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>Under 15kg</span> 50mg/kg once daily for 10 days<br> <span class=\'age-group\'> 15 - 29.9kg</span> 750mg once daily for 10 days<br><span class=\'age-group\'> 30kg or over</span> 1,000mg once daily for 10 days</div></div>',
             'https://nzfchildren.org.nz/nzf_3025', True, 2, 40, 1000, True, 'once daily for 10 days', 2, 50, 40, 1000, None, None, None, None, None, None),
            ('Amoxicillin250', 2, False, 0.3, 15, 'three times a day', 20, 1000, False, None, None, None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15 - 30mg/kg (maximum 1,000mg) three times daily </div> <strong>Strep A Dosing:</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>Under 15kg</span> 50mg/kg once daily for 10 days<br> <span class=\'age-group\'> 15 - 29.9kg</span> 750mg once daily for 10 days<br><span class=\'age-group\'> 30kg or over</span> 1,000mg once daily for 10 days</div></div>',
             'https://nzfchildren.org.nz/nzf_3025', True, 2, 20, 1000, True, 'once daily for 10 days', 1, 50, 20, 1000, None, None, None, None, None, None),
            ('Cefaclor125', 2, False, 0.4, 10, 'three times a day', 20, 500, False, None, None, None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br><div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 10 mg/kg (maximum 500 mg) three times daily </div></div>',
             'https://nzfchildren.org.nz/nzf_3052', False, None, None, None, False, '', None, None, None, None, None, None, None, None, None, None),
            ('Cefalexin125multi', 2, False, 0.5, 12.5, '(12.5 or 25 mg/kg, see below for indication and frequency)', 40,
             1000, False, None, None, None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>Acute uncomplicated UTIs:</strong> <br><div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 25 mg/kg (maximum 500mg) THREE times daily for three days; or seven days in moderate to severe infection <span class=\'age-group\'></div> <strong>Mild to moderate cellulitis:</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 12.5 mg/kg (maximum 1 g) TWO to FOUR times daily for five days</div><strong>Impetigo with extensive or multiple lesions:</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 12.5 - 25 mg/kg (maximum 1 g) TWICE daily</div></div>',
             'https://nzfchildren.org.nz/nzf_3058', True, 2, 40, 1000, False, '', None, None, None, None, None, None, None, None, None, None),
            (
            'Cefalexin250multi', 2, False, 0.25, 12.5, '(12.5 or 25 mg/kg, see below for indication and frequency)', 20,
            1000, False, None, None, None, None,
            '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>Acute uncomplicated UTIs:</strong> <br><div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 25 mg/kg (maximum 500mg) THREE times daily for three days; or seven days in moderate to severe infection <span class=\'age-group\'></div> <strong>Mild to moderate cellulitis:</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 12.5 mg/kg (maximum 1 g) TWO to FOUR times daily for five days</div><strong>Impetigo with extensive or multiple lesions:</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 12.5 - 25 mg/kg (maximum 1 g) TWICE daily</div></div>',
            'https://nzfchildren.org.nz/nzf_3058', True, 2, 40, 1000, False, '', None, None, None, None, None, None, None, None, None, None),
            ('Cefalexin125', 2, False, 0.5, 12.5, 'twice <b>OR</b> four times a day', 40, 1000, False, None, None, None,
             None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br><div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 12.5-25 mg/kg (usual maximum 500 mg; up to 1 g may be used), <strong>TWICE</strong> daily for superficial skin infections and <strong>FOUR</strong> times daily for infections due to sensitive Gram-positive and Gram-negative bacteria <br> <span class=\'age-group\'> Note</span> High doses (25 mg/kg) are used in secondary care situations (e.g. step-down dosing from intravenous to oral therapy for bone and joint infections).</div></div>',
             'https://nzfchildren.org.nz/nzf_3058', False, None, None, None, False, '', None, None, None, None, None, None, None, None, None, None),


            ('Cefalexin250', 2, False, 0.25, 12.5, 'twice <b>OR</b> four times a day', 20, 1000, False, None, None, None,
            None,
            '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br><div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 12.5-25 mg/kg (usual maximum 500 mg; up to 1 g may be used), <strong>TWICE</strong> daily for superficial skin infections and <strong>FOUR</strong> times daily for infections due to sensitive Gram-positive and Gram-negative bacteria <br> <span class=\'age-group\'> Note</span> High doses (25 mg/kg) are used in secondary care situations (e.g. step-down dosing from intravenous to oral therapy for bone and joint infections).</div></div>',
            'https://nzfchildren.org.nz/nzf_3058', False, None, None, None, False, '', None, None, None, None, None, None, None, None, None, None),
            ('Coamoxiclav125-31.25', 2, False, 0.48, 15, 'three times a day', 20, 625, False, None, None, None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br><div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15-30 mg/kg (maximum 625 mg) 3 times daily <br> <span class=\'age-group\'> Note</span> Oral doses are expressed as the total dose of amoxicillin + clavulanic acid (ratio 4:1); 15-30 mg of the total (amoxicillin + clavulanic acid) contains 12-24 mg of amoxicillin. </div> <strong>Strep A Dosing (Third or More Episode within 3 months):</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>Child</span>  16.7 mg/kg (maximum dose 833 mg) 3 times daily for 10 days (50 mg/kg daily, maximum 2.5 g daily)</div></div>',
             'https://nzfchildren.org.nz/nzf_3032', True, 2, 20, 625, True, 'three times daily for 10 days', 0.533,
             16.7, 26.65, 833, None, None, None, None, None, None),
            ('Coamoxiclav250-62.5', 2, False, 0.24, 15, 'three times a day', 10, 625, False, None, None, None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br><div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15-30 mg/kg (maximum 625 mg) 3 times daily <br> <span class=\'age-group\'> Note</span> Oral doses are expressed as the total dose of amoxicillin + clavulanic acid (ratio 4:1); 15-30 mg of the total (amoxicillin + clavulanic acid) contains 12-24 mg of amoxicillin. </div> <strong>Strep A Dosing (Third or More Episode within 3 months):</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>Child</span>  16.7 mg/kg (maximum dose 833 mg) 3 times daily for 10 days (50 mg/kg daily, maximum 2.5 g daily)</div></div>',
             'https://nzfchildren.org.nz/nzf_3032', True, 2, 10, 625, True, 'three times daily for 10 days', 0.2665,
             16.7, 13.32, 833, None, None, None, None, None, None),
            ('Coamoxiclav125-31.25nostrepinfo', 2, False, 0.48, 15, 'three times a day', 20, 625, False, None, None,
             None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br><div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15-30 mg/kg (maximum 625 mg) 3 times daily <br> <span class=\'age-group\'> Note</span> Oral doses are expressed as the total dose of amoxicillin + clavulanic acid (ratio 4:1); 15-30 mg of the total (amoxicillin + clavulanic acid) contains 12-24 mg of amoxicillin. </div> ',
             'https://nzfchildren.org.nz/nzf_3032', True, 2, 20, 625, True, 'three times daily for 10 days', 0.533,
             16.7, 26.65, 833, None, None, None, None, None, None),
            (
            'Coamoxiclav250-62.5nostrepinfo', 2, False, 0.24, 15, 'three times a day', 10, 625, False, None, None, None,
            None,
            '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br><div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 15-30 mg/kg (maximum 625 mg) 3 times daily <br> <span class=\'age-group\'> Note</span> Oral doses are expressed as the total dose of amoxicillin + clavulanic acid (ratio 4:1); 15-30 mg of the total (amoxicillin + clavulanic acid) contains 12-24 mg of amoxicillin. </div></div>',
            'https://nzfchildren.org.nz/nzf_3032', True, 2, 10, 625, True, 'three times daily for 10 days', 0.2665,
            16.7, 13.32, 833, None, None, None, None, None, None),



            ('Cotrimoxazole480', 2, False, 0.5, 24, 'twice a day', 20, 960, False, None, None, None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>6 weeks - 18 years</span> 24 mg/kg (maximum 960 mg) twice daily </div></div>',
             'https://nzfchildren.org.nz/nzf_3200', False, None, None, None, False, None, None, None, None, None, None, None, None, None, None, None),
            ('Erythromycin200', 2, False, 0.25, 10, 'four times a day', 10, 400, False, 0.5, 20, 20, 800,
             '<div class=\'message__section-dosing-instructions\'><span class=\'age-group\'> Note</span> Erythromycin has two forms: erythromycin ethylsuccinate, and erythromycin stearate. This calculator uses the former, and this should be specified on the prescription</div> <div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 10-12.5 mg/kg every 6 hours (usual maximum 1.6 g daily; maximum 4 g daily in severe infection)</div> <strong>Strep A Dosing:</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>Child</span> 20 mg/kg twice daily; maximum 800 mg twice daily for 10 days</div></div>',
             'https://nzfchildren.org.nz/nzf_3154', True, 1.25, 10, 400, True, 'twice daily for 10 days', 0.5, 20, 25,
             1000, None, None, None, None, None, None),
            ('Erythromycin400', 2, False, 0.125, 10, 'four times a day', 5, 400, False, 0.25, 20, 10, 800,
             '<div class=\'message__section-dosing-instructions\'><span class=\'age-group\'> Note</span> Erythromycin has two forms: erythromycin ethylsuccinate, and erythromycin stearate. This calculator uses the former, and this should be specified on the prescription</div> <div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 10-12.5 mg/kg every 6 hours (usual maximum 1.6 g daily; maximum 4 g daily in severe infection)</div> <strong>Strep A Dosing:</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>Child</span> 20 mg/kg twice daily; maximum 800 mg twice daily for 10 days</div></div>',
             'https://nzfchildren.org.nz/nzf_3154', True, 1.25, 5, 400, True, 'twice daily for 10 days', 0.25, 20, 2.5,
             1000, None, None, None, None, None, None),
            ('Flucloxacillin125', 2, False, 0.5, 12.5, 'four times a day', 20, 500, False, None, None, None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 12.5-25 mg/kg (usually up to 500 mg; maximum 1 g) 4 times daily (see note below) <br> <span class=\'age-group\'> Note</span> High doses (25 mg/kg, maximum 1 g) should be used in severe infection (e.g. step-down therapy from intravenous to oral dosing, or deep site infection). High oral doses may be poorly tolerated due to gastrointestinal adverse effects.</div></div>',
             'https://nzfchildren.org.nz/nzf_3012', False, None, None, None, False, None, None, None, None, None, None, None, None, None, None, None),
            ('Flucloxacillin250', 2, False, 0.25, 12.5, 'four times a day', 10, 500, False, None, None, None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 12.5-25 mg/kg (usually up to 500 mg; maximum 1 g) 4 times daily (see note below) <br> <span class=\'age-group\'> Note</span> High doses (25 mg/kg, maximum 1 g) should be used in severe infection (e.g. step-down therapy from intravenous to oral dosing, or deep site infection). High oral doses may be poorly tolerated due to gastrointestinal adverse effects.</div></div>',
             'https://nzfchildren.org.nz/nzf_3012', False, None, None, None, False, None, None, None, None, None, None, None, None, None, None, None),
            ('Lactulose', 3, False, 0.5, 0.334, 'twice daily (adjusted according to response)', 20, 20, False, None,
             None, None, None,
             '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 1 years</span> 2.5 mL twice daily, adjusted according to response<br><span class=\'age-group\'>1 - 5 years</span> 2.5-10 mL twice daily, adjusted according to response<br><span class=\'age-group\'>5 - 18 years</span> 5-20 mL twice daily, adjusted according to response <br> <span class=\'age-group\'> Note</span> This calculator uses the UpToDate dosing of 0.5 mL/kg</div></div>',
             'https://nzfchildren.org.nz/nzf_895', False, None, None, None, False, None, None, None, None, None, None, None, None, None, None, None),


('Macrogol', 3, False, 0.038, 0.5, 'daily', 8, 105, False, None, None, None, None,
 '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>12 - 18 years</span> 1 sachet once daily, increase to 2-3 sachets daily if required; contents of each sachet dissolved in half a glass (approximately 125 mL) of water<br><span class=\'age-group\'>2 - 18 years</span> The NZF only provides dosing advise for the unfunded Lax-Sachets Half for this age group. Therefore this calculator uses 1.5g/kg for disimpaction (<a href=\'https://www.starship.org.nz/for-health-professionals/starship-clinical-guidelines/c/constipation/\' target=\'_blank\'>starship</a> advises 1-1.5g/kg), and a maintenance dose of 0.5g/kg </div></div>',
 'https://nzfchildren.org.nz/nzf_897', False, None, None, None, False, None, None, None, 8, 105, None, None, None, None, None, None),
]

            # ('Loratadine', 3, False, None, None, 'once a day', None, None, False, None, None, None, None,
            #  '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 - 2 years</span> 2.5 mg once daily<br><span class=\'age-group\'>2 - 12 years under 30kg</span> 5 mg once daily<br><span class=\'age-group\'>2 - 12 years over 30kg</span> 10 mg once daily<br> <span class=\'age-group\'>12 - 18 years</span> 10 mg once daily</div></div>',
            #  'https://nzfchildren.org.nz/nzf_1848', True, None, None, None, False, None, 30, 9999, 5, 5, 10, 10,
            #  '<br><br>(2.5 mLs if 1-2 years)', '<br><br>(2.5 mgs if 1-2 years)'),

            # ('Penicillin125', 2, False, 0.25, 6.25, 'four times a day', 20, 500, False, None, None, None, None,
            #  '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 6.25-12.5 mg/kg (maximum 250-500 mg) 4 times daily </div><strong>Strep A Dosing (First and Second Episodes):</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'> Under 20kg</span> 250 mg 2-3 times daily for 10 days<br><span class=\'age-group\'> Over 20kg</span> 500 mg 2-3 times daily for 10 days</div><strong>Strep A Dosing (Third or More Episode within 3 months):</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'> Child</span> 12.5 mg/kg (maximum 500 mg) 4 times daily for 10 days, in combination with <a href=\'https://nzfchildren.org.nz/nzf_3243\' target=\'_blank\'>rifampicin</a> at 20 mg/kg (maximum 600 mg) once daily for 4 days, beginning on day 7 of the phenoxymethylpenicillin or amoxicillin course (requires specialist approval)</div></div>',
            #  'https://nzfchildren.org.nz/nzf_3006', True, 2, 20, 500, True, True,
            #  ' two to three times daily for ten days', 10, 20, 10, 500, 20, 500, 250, 500, '', ''),
            # ('Penicillin250', 2, False, 0.125, 6.25, 'four times a day', 10, 500, False, None, None, None, None,
            #  '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>1 month - 18 years</span> 6.25-12.5 mg/kg (maximum 250-500 mg) 4 times daily </div><strong>Strep A Dosing (First and Second Episodes):</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'> Under 20kg</span> 250 mg 2-3 times daily for 10 days<br><span class=\'age-group\'> Over 20kg</span> 500 mg 2-3 times daily for 10 days</div><strong>Strep A Dosing (Third or More Episode within 3 months):</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'> Child</span> 12.5 mg/kg (maximum 500 mg) 4 times daily for 10 days, in combination with <a href=\'https://nzfchildren.org.nz/nzf_3243\' target=\'_blank\'>rifampicin</a> at 20 mg/kg (maximum 600 mg) once daily for 4 days, beginning on day 7 of the phenoxymethylpenicillin or amoxicillin course (requires specialist approval)</div></div>',
            #  'https://nzfchildren.org.nz/nzf_3006', True, 2, 10, 500, True, False,
            #  ' two to three times daily for ten days', 5, 10, 5, 500, 10, 500, 250, 500, '', ''),


            #  ('Prednisolone', 3, False, 0.2, 1, 'once a day', 8, 40, False, None, None, None, None,
            #  '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>Child</span> 1-2 mg/kg (maximum 40 mg) once daily for 3-5 days; if child has been taking an oral corticosteroid for more than a few days, give 2 mg/kg (maximum 60 mg) once daily for at least 5 days </div></div>',
            #  'https://nzfchildren.org.nz/nzf_3846', True, 2, 8, 40, False, None, None, None, None, None, None, None,
            #  None, None, None, None, None,
            #  '<br><br>If child has been taking an oral corticosteroid for more than a few days, give 2 mg/kg (i.e. 0.4mL/kg, with a higher maximum of 12mL) once daily',
            #  '<br><br>If child has been taking an oral corticosteroid for more than a few days, give 2 mg/kg (higher maximum of 60mg) once daily'),
            # # ('Roxithromycin', 2, True, None, 2.5, 'twice daily', None, 150, False, None, None, None, None,
            #  '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>under 40 kg</span> 2.5-4 mg/kg (maximum 150 mg) twice daily <br><span class=\'age-group\'>over 40 kg</span> 150 mg twice daily </div> <strong>Strep A Dosing:</strong> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>under 40 kg</span> 2.5 mg/kg twice daily for 10 days<br> <span class=\'age-group\'> over 40 kg </span> 150 mg twice daily for 10 days<br></div></div>',
            #  'https://nzfchildren.org.nz/nzf_3161', True, 1.6, None, 150, True, False, ' twice daily for 10 days', None,
            #  None, None, None, None, None, None, None, None, None, None, None, '', ''),
            # ('Ferrous_sulphate', 3, False, 0.25, 1.5, 'twice a day', 7.5, 45, False, None, None, None, None,
            #  '<div class=\'message__section-dosing-item message__section-dosing-label\'><strong>General Dosing:</strong> <br> <div class=\'message__section-dosing-instructions\'><span class=\'age-group\'>Child 1 month - 12 years</span> 0.5-1 mL/kg daily up to maximum 30 mL daily in 2-3 divided doses <br><span class=\'age-group\'>Child 12 - 18 years</span> 15-30 mL daily in 1-2 divided doses</div></div>',
            #  'https://nzfchildren.org.nz/nzf_4915', True, 2, 15, 90, False, None, None, None, None, None, None, 0.33, 2,
            #  None, 'daily', '', ' of equivalent elemental iron', None, None, '', ' of equivalent elemental iron')

#Выполняем вставку

    #     cursor.executemany('''INSERT INTO drugs
    # (name, category_id, tablet_only, mls_var, mgs_var, number_of_times_a_day,
    #  mls_max, mgs_max, loading_dose, mls_var_loading, mgs_var_loading,
    #  mls_max_loading, mgs_max_loading, instructions, nzf_link,
    #  high_range, high_modifier, mls_max_high, mgs_max_high,
    #  strep_drug, strep_frequency, mls_var_strep, mgs_var_strep,
    #  mls_strep_max, mgs_strep_max, weight_cutoff_1, weight_cutoff_2, range1_dose, range2_dose, form, age_range)
    # VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', drugs_data)

        products = [
            ('HP Pavilion Laptop', 'Electronics', 10.99, 10),
            ('Samsung Galaxy Smartphone', 'Electronics', 15.99, None),
            ('Adidas T-shirt', 'Clothing', 8.99, 2.50),
            ('Levis Jeans', 'Clothing', 12.99, 15)
            ]
        cursor.executemany("INSERT INTO products (name, category, price, discount) VALUES (?, ?, ?, ?)", products)

        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        # Закрываем соединение
        conn.close()




# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('myapp.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Устанавливаем row_factory для доступа по именам колонок
    cursor = conn.cursor()
    return cursor

# Генератор нового ID
def generate_id():
    return max(book['id'] for book in BOOKS) + 1 if BOOKS else 1

# Удаление книги по ID
def remove_book(book_id):
    global BOOKS
    BOOKS = [book for book in BOOKS if book['id'] != book_id]


# Регистрация нового пользователя
#@app.route('/api/register', methods=['POST'])
#def register_user():
 #   data = request.get_json()
  #  username = data.get('username')
   # password = data.get('password')
    #if not username or not password:
     #   return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400
    #USERS.append({'username': username, 'password': password})
    #return jsonify({'status': 'success', 'message': 'User registered successfully'}), 201

@app.route('/api/register', methods=['POST'])
def register_user():
    conn = sqlite3.connect('myapp.db')
    cursor = conn.cursor()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        return jsonify({'message': 'User already exists'}), 400
    ##ДОБАВИТЬ ПРОВЕРКУ ПО ПОЧТЕ НА УНИКАЛЬНОСТЬ

    cursor.execute("INSERT INTO users (username,email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
    conn.commit()

    return jsonify({'message': 'User registered successfully'}), 201



# Вход пользователя
#@app.route('/api/login', methods=['POST'])
#def login_user():
 #   data = request.get_json()
  #  username = data.get('username')
   # password = data.get('password')
    #if not username or not password:
     #   return jsonify({'status': 'error', 'message': 'Username and password are required'}), 400
    #user = next((user for user in USERS if user['username'] == username and user['password'] == password), None)
    #if user:
     #   access_token = create_access_token(identity=username)  # Создание токена
      #  return jsonify({'status': 'success', 'access_token': access_token}), 200
    #else:
     #   return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401


@app.route('/api/login', methods=['POST'])
def login_user():
    conn = sqlite3.connect('myapp.db')
    cursor = conn.cursor()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, hashed_password))
    user = cursor.fetchone()

    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
        # Получаем user_id
    user_id = user[0]
    access_token = create_access_token(identity=username)
    # Возвращаем токен и user_id
    return jsonify(access_token=access_token, user_id=user_id), 200

###Calculator
@app.route('/api/drugs', methods=['GET'])
#@jwt_required()  # Защищаем маршрут JWT-токеном
def get_drugs():
    cursor = get_db_connection()
    try:
        # Выполняем SQL-запрос
        cursor.execute('''
            SELECT d.id, d.name, d.tablet_only, d.mls_var, d.instructions, dc.category_name
            FROM drugs d
            JOIN drugs_categories dc ON d.category_id = dc.category_id
            ORDER BY dc.category_name, d.name
        ''')
        drugs = cursor.fetchall()

        # Группируем препараты по категориям
        drugs_by_categories = {}
        for drug in drugs:
            category_name = drug['category_name']
            if category_name not in drugs_by_categories:
                drugs_by_categories[category_name] = []
            drugs_by_categories[category_name].append({
                'id': drug['id'],
                'name': drug['name'],
                'tablet_only': drug['tablet_only'],
                'mls_var': drug['mls_var'],
                'instructions': drug['instructions']
            })

        return jsonify(drugs_by_categories)
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to fetch drugs from the database."}), 500
    finally:
        cursor.connection.close()  # Закрываем соединение через курсор

##Расчет дозировки и сохранение в БД@app.route('/calculate', methods=['POST'])
@app.route('/api/calculate', methods=['POST'])
#@jwt_required()  # Защищаем маршрут JWT-токеном
def calculate_dosage():
    data = request.json
    user_id = data.get('user_id')
    drug_id = data.get('drug_id')
    weight = data.get('weight')
    weight = float(weight)

    # Проверяем наличие обязательных параметров
    if user_id is None or drug_id is None or weight is None:
        return jsonify({'error': 'user_id, drug_id, and weight are required'}), 400

    # Проверяем корректность веса
    if weight <= 0:
        return jsonify({'error': 'Weight must be greater than 0'}), 400

    # Получаем данные о препарате из базы данных
    try:
        conn = sqlite3.connect('myapp.db')
        cursor = conn.cursor()

        # Запрос данных о препарате
        #можно ли тут написать. select *?
        cursor.execute('''SELECT name, category_id, mls_var, mgs_var
                          FROM drugs
                          WHERE id = ?''', (drug_id,))
        drug = cursor.fetchone()

        if not drug:
            conn.close()
            return jsonify({'error': 'Drug not found'}), 404

        # Извлекаем данные из результата запроса
        name, category_id, mls_var, mgs_var = drug

        # Выполняем расчеты
        mls_total = weight * mls_var
        mgs_total = weight * mgs_var

        # Сохраняем расчет в историю
        # Установка значений для всех 23 полей
        cursor.execute('''
            INSERT INTO calculation_history (
                user_id, calculation_id, drug_id, drug_name, username, weight, dosage_mls, dosage_mgs,
                totalMgs, totalhigh, totalhighsachets, maximumMgsPerDay, highMgs,
                loading_dose, strep_drug, messageMgs, messageOther, calculation_type,
                calculation_status, calculation_version, patient_id, patient_name, error_message, age
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)''',
                       (
                           user_id, None, drug_id, name, 'Username', weight, mls_total, mgs_total,
                           0, 0, 0, 0, 0, 0, 0, 'Message', None, category_id,
                           'Status', 'Version', 0, 'Patient Name', None , None
                       ))
        # Получаем автоматически сгенерированный id
        calculation_id = cursor.lastrowid
        # Обновляем запись, чтобы установить calculation_id равным id
        cursor.execute('''
            UPDATE calculation_history
            SET calculation_id = ?
            WHERE id = ?''',
                       (calculation_id, calculation_id))
        conn.commit()


    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

        # Возвращаем ответ с calculation_id
    return jsonify({
            'mlsTotal': mls_total,
            'mgsTotal': mgs_total,
            'calculation_id': calculation_id
        })
    conn.close()

#############
@app.route('/api/calculation-history/', methods=['GET'])
def get_calculation_history():
    user_id = request.args.get('user_id')  # Обязательный параметр
    category_name = request.args.get('category_name')  # Необязательный
    date_from = request.args.get('date_from')  # Необязательный
    date_to = request.args.get('date_to')  # Необязательный

    # Проверяем наличие обязательного параметра
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    try:
        conn = sqlite3.connect('myapp.db')
        cursor = conn.cursor()

        # Формируем SQL-запрос с JOIN
        query = '''SELECT ch.*
                   FROM calculation_history ch
                   JOIN drugs_categories dc ON ch.calculation_type = dc.category_id
                   WHERE ch.user_id = ?'''
        params = [user_id]

        # Добавляем фильтры, если они переданы
        if category_name:
            query += ' AND dc.category_name = ?'
            params.append(category_name)

        if date_from and date_to:
            query += ' AND ch.created_at BETWEEN ? AND ?'
            params.extend([date_from, date_to])

        # Выполняем запрос
        cursor.execute(query, params)
        history = cursor.fetchall()

        # Преобразуем данные в формат JSON
        result = []
        for row in history:
            result.append({
                'id': row[0],  # id
        'user_id': row[2],  # user_id
        'drug_name': row[4],  # drug_name
        'calculation_type': row[15],
        'weight': row[6],       # calculation_type
        'mls': row[7],  # dosage_mls
        'mgs': row[8],  # dosage_mgs
        'created_at': row[24]  # calculation_time
    })
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        conn.close()
 ########


@app.route('/api/books', methods=['GET'])
#@jwt_required()
def user_books():
    conn = get_db_connection()
    cursor = conn.cursor()
    current_user = get_jwt_identity()  # Получаем идентификатор текущего пользователя из токена
    user_books = [book for book in BOOKS if book.get('username') == current_user]  # Фильтруем книги по текущему пользователю
    return jsonify({'status': 'success', 'books': user_books})

# Добавление новой книги
@app.route('/api/books', methods=['POST'])
#@jwt_required()
def add_book():
    conn = get_db_connection()
    cursor = conn.cursor()
    current_user = get_jwt_identity()  # Получаем идентификатор текущего пользователя из токена
    data = request.get_json()
    new_book = {
        'id': generate_id(),
        'title': data.get('title'),
        'author': data.get('author'),
        'read': data.get('read'),
        'username': current_user  # Сохраняем имя текущего пользователя как владельца книги
    }
    BOOKS.append(new_book)
    return jsonify({'status': 'success', 'message': 'Book added!', 'book': new_book}), 201

# Получение, обновление или удаление конкретной книги по ее ID
@app.route('/api/books/<int:book_id>', methods=['GET', 'PUT', 'DELETE'])
#@jwt_required()
def single_book(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    current_user = get_jwt_identity()  # Получаем имя текущего пользователя из токена
    book = next((book for book in BOOKS if book['id'] == book_id), None)
    if not book:
        return jsonify({'status': 'error', 'message': 'Book not found'}), 404

    # Проверяем, принадлежит ли книга текущему пользователю
    if book['username'] != current_user:
        return jsonify({'status': 'error', 'message': 'You do not have permission to access this book'}), 403

    if request.method == 'PUT':
        post_data = request.get_json()
        remove_book(book_id)
        updated_book = {
            'id': book_id,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read'),
            'username': current_user  # Сохраняем имя текущего пользователя как владельца книги
        }
        BOOKS.append(updated_book)
        return jsonify({'status': 'success', 'message': 'Book updated!', 'book': updated_book})
    elif request.method == 'DELETE':
        remove_book(book_id)
        return jsonify({'status': 'success', 'message': 'Book removed!'})
    else:
        return jsonify({'status': 'success', 'book': book})



# Запуск приложения
if __name__ == '__main__':
    # Инициализация базы данных
    initialize_database()

    # Настройка JWT
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Замените 'your-secret-key' на ваш секретный ключ
    jwt = JWTManager(app)
    # Настройка CORS
    CORS(app)
    app.run()
    # Список книг (заглушка для примера)
    BOOKS = []
    # Список пользователей (заглушка для примера)
    USERS = [
        {
            'username': 'test@test.ru',
            'password': 'test'
        }
    ]