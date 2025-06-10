import streamlit as st
import requests


API_BASE = "http://localhost:5000"

st.set_page_config(
    page_title="SmartCart",
    page_icon="🛒",
    layout="wide",
)

#cache για τις συναρτήσεις scrapping
@st.cache_data() 
def get_masoutis_price(product_id):
    try:
        res = requests.get(f"{API_BASE}/products/{product_id}/scrape/masoutis", timeout=20) #μεγάλο timeout για να προλάβει να ανοίξει ο browser και να επιστρψει την τιμή
        if res.status_code == 200:
            return res.json().get("masoutis_price")
    except:
        return None

@st.cache_data()
def get_sklavenitis_price(product_id):
    try:
        res = requests.get(f"{API_BASE}/products/{product_id}/scrape/sklavenitis", timeout=20) #το ίδιο και εδώ
        if res.status_code == 200:
            return res.json().get("sklavenitis_price")
    except:
        return None


title_col, btn_col = st.columns([6, 1])
with title_col:
    st.title("Καλώς ήρθες στο SmartCart!") #τίτλος σελίδας

with btn_col:
    if st.button("Δες το καλάθι σου", key="btn_view_cart"): #αν πατηθεί το κουμπί "Δες το καλάθι σου"
     st.session_state["show_cart"] = True

    if st.session_state.get("show_cart"):
        cart_id = st.session_state.get("cart_id")
        if cart_id:
            try:
                response = requests.get(f"{API_BASE}/cart/{cart_id}/open") #καλούμε το api για να ανοίξει το καλάθι
                if response.status_code == 200:
                    cart_data = response.json().get("cart", [])
                    if not cart_data:
                        st.info("Το καλάθι σου είναι άδειο.")
                    else:
                        st.subheader("Το καλάθι μου:")
                        updated = False  # flag για ανανέωση

                        for idx, item in enumerate(cart_data): #για κάθε προιον που υπάρχει στο καλάθι
                            with st.container():
                                st.markdown(f"**{item['name']}** - {item['quantity']} τεμ.") #εμφνίζουμε το προιον
                                qty = st.number_input(  #μπορούμε να αλλάξοθμε ποσότητα
                                    f"Νέα ποσότητα για {item['name']}",
                                    min_value=1,
                                    value=item["quantity"],
                                    key=f"qty_{item['name']}_{idx}"
                                )

                                if st.button("Ενημέρωση", key=f"update_btn_{item['name']}_{idx}"):
                                    update_res = requests.put(
                                        f"{API_BASE}/cart/{cart_id}/update", #αν γίνει αλλαγή καλείται το αντίστοιχο update api
                                        json={"name": item["name"], "quantity": qty},
                                        timeout=5
                                    )
                                    if update_res.status_code == 200:
                                        st.success("Η ποσότητα ενημερώθηκε!")
                                        st.rerun()
                                    else:
                                        st.error(update_res.json().get("error", "Σφάλμα"))

                        if st.button("Ολοκλήρωση Αγοράς", key="purchase_btn"):  
                            buy_res = requests.post(f"{API_BASE}/cart/{cart_id}/purchase") #αν πατηθεί το "Ολοκληρωση αγοράς" καλείται το api purchase
                            if buy_res.status_code == 200:
                                msg = buy_res.json().get("message")
                                st.success(f"{msg}")
                                st.session_state["show_cart"] = False  #κρύβουμε το καλάθι που δεν χρειάζεται πλέον
                                st.rerun()
                            else:
                                st.error(buy_res.json().get("error", "Αποτυχία αγοράς"))

                        if st.button("Διαγραφή καλαθιού", key="delete_cart_btn"):
                            del_res = requests.delete(f"{API_BASE}/cart/{cart_id}") #κλήση για το delete
                            if del_res.status_code == 200:
                                st.success("Το καλάθι διαγράφηκε.")
                                del st.session_state["cart_id"]
                                st.session_state["show_cart"] = False #κρύβουμε το καλάθι που δεν χρειάζεται πλέον
                                st.rerun()
                            else:
                                st.error("Σφάλμα κατά τη διαγραφή καλαθιού.")
                                
                        if st.button("Είναι υγιεινές οι επιλογές μου;", key="btn_healthy_check"): #έλεγχος με groq για τα προιοντα του καλαθιού
                             try:
                                 response = requests.post(f"{API_BASE}/healthy_option/{cart_id}", timeout=10)
                                 if response.status_code == 200:
                                     healthy_info = response.json().get("Κατα πόσο είναι υγεινά;", "Δεν επιστράφηκε αξιολόγηση.")
                                     st.session_state["healthy_feedback"] = healthy_info
                                 else:
                                     st.session_state["healthy_feedback"] = "Δεν ήταν δυνατός ο έλεγχος"
                             except Exception as e:
                                 st.session_state["healthy_feedback"] = f"Σφάλμα: {e}"

                        # Εμφάνιση αποτελέσματος
                        if st.session_state.get("healthy_feedback"):
                             st.info(st.session_state["healthy_feedback"])

                else:
                    st.error("Αποτυχία φόρτωσης καλαθιού.")
            except Exception as e:
                st.error(f"Σφάλμα: {e}")
        else:
         st.warning("Δεν έχει δημιουργηθεί καλάθι ακόμα.")
         
    if st.button("Δημιούργησε αυτόματα ένα καλάθι", key="btn_auto_cart"): #δυνατότητα αυτόματης δημιουργίας καλαθιού
        try:
            res = requests.get(f"{API_BASE}/auto-cart")
            res.raise_for_status()
            data = res.json()
            st.session_state["cart_id"] = data['cart_id']  #βάζουμε ID στο session
            st.session_state["show_cart"] = True  #ενεργοποιούμε την προβολή του καλαθιού
            st.rerun()
        except Exception as e:
            st.error(f"Σφάλμα: {e}")

if "cart_id" not in st.session_state: #εάν δεν υπάρχει ήδη καλάθι
    res = requests.post("http://localhost:5000/cart") #δημιουργούμε ένα καλώντας το api
    st.session_state["cart_id"] = res.json().get("Δημιουργήθηκε νέο καλάθι με id")
    
with st.container(): #φτιάχνουμε την γραμμή φίλτρων
    cols = st.columns([2, 2, 2, 2])
    with cols[0]:
        search = st.text_input("Όνομα προϊόντος", "") 
    with cols[1]:
        category = st.selectbox("Κατηγορία", ["", "Αλεύρι", "Αλλαντικά", "Αυγά", "Βούτυρο", "Γάλα", "Γιαουρτι", "Τυρί"])
    with cols[2]:
        min_price = st.number_input("Ελάχιστη τιμή", value=0.0, step=0.5)
    with cols[3]:
        max_price = st.number_input("Μέγιστη τιμή", value=100.0, step=0.5)

sort = st.selectbox("Ταξινόμηση κατά", ["name_asc", "name_desc", "price_asc", "price_desc"])

# Φόρτωση προιόντων αυτόματα με βάση τα φίλτρα 
params = {
    "search_name": search,
    "category": category,
    "min_price": min_price,
    "max_price": max_price,
    "sort": sort
}

try:
    res = requests.get(f"{API_BASE}/products", params=params) #στέλνουμε τις παραπάνω παραμέτρους στο api
    res.raise_for_status() #ελέγχουμε μην τυχόν επιστρέψει σφάλμα
    products = res.json() #μεταρέπουμε το json που παίρνουμε σε αντικείμενο

    if not products:
        st.warning("Δεν βρέθηκαν προιόντα.")
    else:
        for prod in products: #για κάθε ένα προιον που επιστρέφει το api
            with st.container(): 
                cols = st.columns([1, 3]) #χωρίζουμε σε στήλες με τη δεύτερη να είναι πιο πλατιά απο την πρώτη
                with cols[0]: #εικόνα των προιόντων
                    image_url = f"{API_BASE}/images/{prod['image']}"
                    st.image(image_url, width=140)
                with cols[1]: 
                    st.subheader(prod["name"])
                    st.caption(prod["category"])
                    st.write(prod["description"])
                    st.markdown(f"{prod['price']}")
                
                    quantity_key = f"quantity_{prod['id']}"
                    quantity = st.number_input(
                    "Ποσότητα", min_value=1, step=1, value=1, key=quantity_key
                    )
    
                    add_key = f"btn_add_to_cart_{prod['id']}"
                    success_key = f"success_{prod['id']}"
                
                    if st.button("Προσθήκη στο καλάθι", key=add_key): #αν πατηθεί το κουμπί "Προσθήκη στο καλάθι"
                       cart_id = st.session_state.get("cart_id")
                       if cart_id:
                        try:
                            response = requests.post(
                            f"{API_BASE}/cart/{cart_id}/add",
                            json={"name": prod["name"], "quantity": quantity}, 
                            timeout=5
                            )
                            if response.status_code == 200:
                                st.session_state[success_key] = True
                            else:
                                st.error(f"{response.json().get('error', 'Αποτυχία προσθήκης')}")
                        except Exception as e:
                            st.error(f"Σφάλμα κατά την αγορά: {e}")
                       else:
                         st.warning("Δεν υπάρχει καλάθι για να ολοκληρωθεί η αγορά.")
                         
                    if st.session_state.get(success_key):
                     st.success("✅ Το προιόν προστέθηκε στο καλάθι")
                        
                    button_key = f"btn_show_prices_{prod['id']}"        
                    state_key = f"state_show_prices_{prod['id']}"       
            
                    if st.button("🔍 Ανακάλυψε τις τιμές της αγοράς", key=button_key): #scrapper
                     st.session_state[state_key] = True

                    # εμφάνιση τιμών αν πατηθεί το παραπάνω
                    if st.session_state.get(state_key, False):
                        with st.spinner("Αναζήτηση τιμών..."):
                         mas_price = get_masoutis_price(prod['id'])
                         skl_price = get_sklavenitis_price(prod['id'])

                        if mas_price is not None:
                         st.success(f"Τιμή Μασούτης: {mas_price}")
                        else:
                         st.warning("Δεν βρέθηκε τιμή Μασούτη")

                        if skl_price is not None:
                         st.success(f"Τιμή Σκλαβενίτης: {skl_price}")
                        else:
                         st.warning("Δεν βρέθηκε τιμή Σκλαβενίτη")
                         
                    recipe_button_key = f"btn_recipe_{prod['id']}"
                    recipe_state_key = f"state_recipe_{prod['id']}"
                    recipe_result_key = f"recipe_result_{prod['id']}"
                    if st.button("Τι θα μαγειρέψουμε σήμερα;", key=recipe_button_key): #Groq για προτάσεις συνταγών
                     try:
                         recipe_res = requests.post(f"{API_BASE}/find_recipe/{prod['id']}", timeout=10)
                         if recipe_res.status_code == 200:
                             result = recipe_res.json().get("Συνταγή", "Δεν επιστράφηκε συνταγή.")
                             st.session_state[recipe_result_key] = result
                         else:
                             st.session_state[recipe_result_key] = "Δεν βρέθηκε συνταγή."
                     except Exception as e:
                         st.session_state[recipe_result_key] = f"Σφάλμα: {e}"

                     # Εμφάνιση αποτελέσματος αν υπάρχει
                     if st.session_state.get(recipe_result_key):
                          st.info(st.session_state[recipe_result_key])
                            
            st.markdown("---")

except requests.exceptions.RequestException as e:
    st.error(f"Σφάλμα σύνδεσης με το API: {e}")