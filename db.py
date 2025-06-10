import sqlite3
connection = sqlite3.connect("smartcart.db")

cursor = connection.cursor()


cursor.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, name TEXT NOT NULL, description TEXT, image TEXT, price REAL)")
# data= [
   # ("Αλλαντικά", "Φιλέτο Γαλοπούλα Καπνιστή", "Υφαντής Φιλέτο Γαλοπούλας Καπνιστό Σε Φέτες Χωρίς Γλουτένη 160γρ." , "Ifantis_galopoula_kapnisti.jpg",2), 
   # ("Αλλαντικά", "Πάριζα", "Creta Farms Εν Ελλάδι Πάριζα Σε Φέτες Χωρίς Γλουτένη 160γρ." , "Creta_Farms_Pariza.jpg",2.5),
   # ("Αλλαντικά", "Μπέικον Καπνιστό", "Νίκας Μπέικον Καπνιστό Σε Φέτες Χωρίς Γλουτένη 100γρ." , "Bacon_Nikas.png",2.12),
   # ("Γάλα", "Γάλα Πλήρες", "Νουνού Family Γάλα Πλήρες 3,6% Λιπαρά Υψηλής Θερμικής Επεξεργασίας 1lt." , "Nounou_Family.png",1.98),
   # ("Γάλα", "Γάλα Ελαφρύ", "Δέλτα Μμμmilk Οικογενειακό Γάλα Ελαφρύ 1,5% Λιπαρά Υψηλής Θερμικής Επεξεργασίας 1lt." , "Delta_MmilkOikogeniako.jpg",2.04),
   # ("Γιαούρτι", "Γιαούρτι Στραγγιστό", "Φάγε Total Γιαούρτι Στραγγιστό 2% Λιπαρά 3x200γρ." , "Total_giaourti.jpg",3.62),
   # ("Τυρί", "Gouda", "Νουνού Gouda Σε Φέτες 200γρ." , "Gouda_nounou.png",2.98),
   # ("Τυρί", "Mozzarella Τριμμένη", "Arla Mozzarella Τριμμένη 200γρ." , "mozzarella_arla.jpg",3.45),
   # ("Βούτυρο", "Βούτυρο Ανάλατο", "Lurpak Βούτυρο Ανάλατο 250γρ." , "Lurpak.jpg",4.12),
   # ("Αυγά", "Χρυσά Αυγά", "Χρυσά Αυγά Φρέσκα Medium 6x53-63γρ." , "xrysa_ayga.jpg",3.01),
   # ("Αλεύρι", "Αλεύρι Για Όλες Τις Χρήσεις", "Αλλατίνη Αλεύρι Για Όλες Τις Χρήσεις 1kg." , "aleuri_allatini.jpg", 1.52)
    #]
#cursor.executemany("INSERT INTO products (category, name, description, image, price)  VALUES(?, ?, ?, ?, ?)", data)

#for row in cursor.execute("SELECT category, name, description, image FROM products"):
    #print(row) -- Έλεγχος κατά τη διάρκεια της δημιουργίας της βάσης

#cursor.execute("ALTER TABLE products ADD COLUMN stock INTEGER NOT NULL DEFAULT 50") #Προστέθηκε το απόθεμα των ππροιοντων στον πίνακα products με αρικό απόθεμα κάθε προιοντος 50
  
#cursor.execute("CREATE TABLE IF NOT EXISTS carts (id INTEGER PRIMARY KEY AUTOINCREMENT, status TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
cursor.execute("CREATE TABLE IF NOT EXISTS CartItems (id INTEGER PRIMARY KEY AUTOINCREMENT, cart_id INTEGER NOT NULL, product_id INTEGER NOT NULL, quantity INTEGER NOT NULL, FOREIGN KEY (cart_id) REFERENCES carts(id), FOREIGN KEY (product_id) REFERENCES products(id))")
#cursor.execute("CREATE TABLE IF NOT EXISTS Purchases (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, total REAL)")
cursor.execute("CREATE TABLE IF NOT EXISTS PurchaseItems (id INTEGER PRIMARY KEY AUTOINCREMENT, purchase_id INTEGER, product_id INTEGER, quantity INTEGER, price REAL, FOREIGN KEY (purchase_id) REFERENCES Purchases(id), FOREIGN KEY (product_id) REFERENCES products(id))")

#Χρειάστηκε να κάνουμε αλλαγή τους δυο πίνακες για να εμφανίζεται η σωστή ώρα στα καλάθια και στις αγορές γιατί με το DEFAULT εμφανίζει 3 ώρες πριν
#cursor.execute("UPDATE carts SET created_at = datetime(created_at, 'localtime')") #Αλλάζω πρώτα τα δεδομένα των carts που έχω ήδη στη βάση μου
#cursor.execute("UPDATE Purchases SET timestamp = datetime(timestamp, 'localtime')") #αντίστοιχα και των purchases
#κρατάμε τα δεδομενα που ήδη έχουμε σε 2 νέους πινακες ώσπου να κάνουμε την αλλαγή και μετά τους κάνουμε drop
#cursor.execute("ALTER TABLE carts RENAME TO carts_old;")
cursor.execute("CREATE TABLE IF NOT EXISTS carts (id INTEGER PRIMARY KEY AUTOINCREMENT, status TEXT NOT NULL, created_at TIMESTAMP DEFAULT (datetime('now','localtime')))")
#cursor.execute("INSERT INTO carts (id, status, created_at) SELECT id, status, created_at FROM carts_old;")
#cursor.execute("DROP TABLE carts_old;")
#cursor.execute("ALTER TABLE Purchases RENAME TO Purchases_old;")
cursor.execute("CREATE TABLE IF NOT EXISTS Purchases (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TIMESTAMP DEFAULT (datetime('now','localtime')), total REAL)")
#cursor.execute("INSERT INTO Purchases (id, timestamp, total) SELECT id, timestamp, total FROM Purchases_old;")
#cursor.execute("DROP TABLE Purchases_old;")

connection.commit()  
cursor.close()
connection.close()