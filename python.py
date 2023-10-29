from streamlit_option_menu import option_menu
import streamlit as st
import re
import cv2
import numpy as np
import pickle
import pandas as pd
import easyocr
import pymysql
from sqlalchemy import create_engine
reader = easyocr.Reader(['en'])


# Database setup
connection_string = "mysql+mysqlconnector://root:123456789@localhost/bizcard"
engine = create_engine(connection_string)

st.set_page_config(page_title="BizCard", page_icon="random", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("BizCard")

def data_extract(extract):
    for i in range(len(extract)):
        extract[i] = extract[i].rstrip(' ')
        extract[i] = extract[i].rstrip(',')
    result = ' '.join(extract)

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    website_pattern = r'[www|WWW|wwW]+[\.|\s]+[a-zA-Z0-9]+[\.|\][a-zA-Z]+'
    phone_pattern = r'(?:\+)?\d{3}-\d{3}-\d{4}'
    phone_pattern2 = r"(?:\+91[-\s])?(?:\d{4,5}[-\s])?\d{3}[-\s]?\d{4}"
    name_pattern = r'[A-Za-z]+\b'
    designation_pattern = r'\b[A-Za-z\s]+\b'
    address_pattern = r'\d+\s[A-Za-z\s,]+'
    pincode_pattern = r'\b\d{6}\b'

    name = designation = company = email = website = primary = secondary = address = pincode = None

    try:
        email = re.findall(email_pattern, result)[0]
        result = result.replace(email, "")
        email = email.lower()
    except IndexError:
        email = None

    try:
        websites = re.findall(website_pattern, result)
        if websites:
            website = websites[0]  # Take the first match
            result = result.replace(website, "")
            website = re.sub('[WWW|www|wwW]+ ', 'www.', website)
            website = website.lower()
        else:
            website = None
    except IndexError:
        website = None
    phone = re.findall(phone_pattern, result)
    if len(phone) == 0:
        phone = re.findall(phone_pattern2, result)
    primary = None
    secondary = None
    if len(phone) > 1:
        primary = phone[0]
        secondary = phone[1]
        for i in range(len(phone)):
            result = result.replace(phone[i], '')
    elif len(phone) == 1:
        primary = phone[0]
        result = result.replace(phone[0], '')

    try:
        pincode = int(re.findall(pincode_pattern, result)[0])
        result = result.replace(str(pincode), '')
    except:
        pincode = 0
    name = re.findall(name_pattern, result)[0]
    name = extract[0]
    result = result.replace(name, '')
    designation = re.findall(designation_pattern, result)[0]
    designation = extract[1]
    result = result.replace(designation, '')
    address = ''.join(re.findall(address_pattern, result))
    result = result.replace(address, '')
    company = extract[-1]
    result = result.replace(company, '')


    # print('Email:', email)
    # print('Website:', website)
    # print('Phone:', phone)
    # print('Primary:', primary)
    # print('Secondary:', secondary)
    # print('Name:', name)
    # print('Designation:', designation)
    # print('Address:', address)
    # print('Pincode:', pincode)
    # print('company:', company)
    # print('remaining:', result)

    info = [name, designation, company, email, website, primary, secondary, address, pincode, result]
    return (info)


# Using object notation
with st.sidebar:
    selected = option_menu(
        menu_title="Navigaton",  # required
        options=["Home","---","Upload", "View/Modify", "---", "About"],  # required
        icons=["house","", "upload","binoculars",  "", "envelope"],  # optional
        menu_icon="person-vcard",  # optional
        default_index=0,  # optional
        styles={"nav-link": {"--hover-color": "brown"}},
        orientation="vertical",
    )
if selected == 'Home':
    st.subheader("Welcome to the BizCard Project! ")
    st.markdown("__<p>We are here to introduce you to an innovative solution that will transform the way you manage "
                "your contact information. Our project is centered around simplifying the process of storing and "
                "accessing business cards by creating a digital database.</p>__ "
                "<br>"
                "__<p>Gone are the days of manually entering contact details from visiting cards. "
                "With our cutting-edge technology, all you need to do is scan the card using our integrated scanner, "
                "and voila! A soft copy of the card is created and securely stored in our database.</p>__ "
                "<br>"
                "__<p>Imagine the convenience of having all your contacts readily available at your fingertips. "
                "No more digging through stacks of business cards or struggling to remember where you put that "
                "important contact. Our system ensures that your contacts are organized and easily searchable, "
                "saving you time and effort.</p>__"
                "<br>"
                "__<p>Not only does our BizCard Project offer a streamlined approach to managing contacts, "
                "but it eliminating the need for physical storage and "
                "reducing the risk of losing important cards, our digital database ensures that your valuable "
                "connections are preserved for the long term.</p>__ "
                "<br>"
                "__<p>We understand the importance of building and nurturing relationships in the business world. "
                "That's why our project empowers you to strengthen your network efficiently. With quick access to "
                "contact information, you can reach out to potential clients, collaborators, or partners effortlessly, "
                "helping you seize every opportunity that comes your way.</p>__ "
                "<br>"
                "__<p>Join us on this journey of revolutionizing contact management. Say goodbye to cluttered desks "
                "and hello to a digital future. Explore our BizCard Project and discover the ease and efficiency of "
                "keeping your contacts in a secure, accessible, and organized format. </p>__"
                "<br>"
                "__<p>Start scanning, start connecting, and start building lasting relationships with the BizCard "
                "Project.</p>__",unsafe_allow_html=True)

elif selected == "Upload":
    uploaded_file = st.file_uploader("Choose a image file", type=["jpg", "jpeg", "png"])
    if uploaded_file != None:
        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
        col1, col2, col3 = st.columns([2, 1, 2])
        with col3:
            st.image(image)
        with col1:
            result = reader.readtext(image, detail=0)
            info = data_extract(result)
            # st.write(info)
            # st.table(pd.Series(info, index=['Name', 'Designation', 'Company', 'Email ID', 'Website', 'Primary Contact', 'Secondary Contact', 'Address', 'Pincode', 'Other']))
            ls_name = st.text_input('Name:', info[0])
            ls_desig = st.text_input('Designation:', info[1])
            ls_Com = st.text_input('Company:', info[2])
            ls_mail = st.text_input('Email ID:', info[3])
            ls_url = st.text_input('Website:', info[4])
            ls_m1 = st.text_input('Primary Contact:', info[5])
            ls_m2 = st.text_input('Secondary Contact:', info[6])
            ls_add = st.text_input('Address:', info[7])
            ls_pin = st.number_input('Pincode:', info[8])
            ls_oth = st.text_input('Others(this will not stored):', info[9])
            a = st.button("upload")
            if a:
                # Establishing the connection and creating the cursor
                conn = pymysql.connect(host='localhost', user='root', password='123456789', db='bizcard')
                cursor = conn.cursor()

                # Now perform the database operations
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS business_cards (name VARCHAR(255), designation VARCHAR(255), "
                    "company VARCHAR(255), email VARCHAR(255), website VARCHAR(255), primary_no VARCHAR(255), "
                    "secondary_no VARCHAR(255), address VARCHAR(255), pincode int, image BLOB)")

                query = "INSERT INTO business_cards (name, designation, company, email, website, primary_no, secondary_no, " \
                        "address, pincode, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                # Convert the numpy image to bytes
                image_bytes = pickle.dumps(image)

                # Use image_bytes in your insert query instead of image.read()
                val = (ls_name, ls_desig, ls_Com, ls_mail, ls_url, ls_m1, ls_m2, ls_add, ls_pin, image_bytes)
                cursor.execute(query, val)
                conn.commit()

                st.success('Contact stored successfully in database', icon="✅")
                st.balloons()

                # Close the connection when done
                cursor.close()
                conn.close()

elif selected == 'View/Modify':
    col1, col2, col3 = st.columns([2, 2, 4])

    with col1:
        conn = pymysql.connect(host='localhost', user='root', password='123456789', db='bizcard')
        cursor = conn.cursor()
        cursor.execute('select name from business_cards')
        y = cursor.fetchall()
        contact = [x[0] for x in y]
        contact.sort()
        selected_contact = st.selectbox('Name', contact)

    with col2:
        mode_list = ['', 'View', 'Modify', 'Delete']
        selected_mode = st.selectbox('Mode', mode_list, index=0)

    if selected_mode == 'View':
        col5, col6 = st.columns(2)
        cursor.execute(f"select name, designation, company, email, website, primary_no, secondary_no, "
                       f"address, pincode from business_cards where name = '{selected_contact}'")
        y = cursor.fetchall()
        st.table(pd.Series(y[0], index=['Name', 'Designation', 'Company', 'Email ID', 'Website', 'Primary Contact',
                                        'Secondary Contact', 'Address', 'Pincode'], name='Card Info'))

    elif selected_mode == 'Modify':
        cursor.execute(f"select name, designation, company, email, website, primary_no, secondary_no, "
                       f"address, pincode from business_cards where name = '{selected_contact}'")
        info = cursor.fetchone()
        col5, col6 = st.columns(2)

        ls_name = st.text_input('Name:', info[0])
        ls_desig = st.text_input('Designation:', info[1])
        ls_Com = st.text_input('Company:', info[2])
        ls_mail = st.text_input('Email ID:', info[3])
        ls_url = st.text_input('Website:', info[4])
        ls_m1 = st.text_input('Primary Contact:', info[5])
        ls_m2 = st.text_input('Secondary Contact:', info[6])
        ls_add = st.text_input('Address:', info[7])
        ls_pin = st.number_input('Pincode:', info[8])

        a = st.button("Update")
        if a:
            query = f"update business_cards set name = %s, designation = %s, company = %s, email = %s, website = %s, " \
                    f"primary_no = %s, secondary_no = %s, address = %s, pincode = %s where name = '{selected_contact}'"
            val = (ls_name, ls_desig, ls_Com, ls_mail, ls_url, ls_m1, ls_m2, ls_add, ls_pin)
            cursor.execute(query, val)
            conn.commit()
            st.success('Contact updated successfully in database', icon="✅")

    elif selected_mode == 'Delete':
        # Your streamlit code for warning...

        confirm = st.button('Confirm')
        if confirm:
            query = f"DELETE FROM business_cards where name = '{selected_contact}'"
            cursor.execute(query)
            conn.commit()
            st.success('Contact removed successfully from database', icon="✅")
            st.balloons()

            cursor.close()
            conn.close()
elif selected == 'About':
    st.markdown('__<p style="text-align:left; font-size: 25px; color: #FAA026">Summary of BizCard Project</P>__',
                unsafe_allow_html=True)
    st.write(
        "This business card project focused on enabling users to scan any visiting card and make a soft copy in "
        "the database. This innovative business card project has revolutionized the way we store contact "
        "information. With its built-in scanner, users can quickly and easily scan any visiting card into a "
        "soft copy, which can be stored in a secure database for quick access. This is an efficient and effective "
        "way to keep track of contacts and build relationships.")
    st.markdown(
        '__<p style="text-align:left; font-size: 20px; color: #FAA026">Applications and Packages Used:</P>__',
        unsafe_allow_html=True)
    st.write("  * Python")
    st.write("  * MYSQl workbench")
    st.write("  * Streamlit")
    st.write("  * Github")
    st.write("  * Pandas, EasyOCR, Re, CV2, pymysql")
    st.markdown(
        '__<p style="text-align:left; font-size: 20px; color: #FAA026">For feedback/suggestion, connect with me on</P>__',
        unsafe_allow_html=True)
    st.subheader("LinkedIn")
    st.write("https://www.linkedin.com/in/shiva-raj-77039822a/")
    st.subheader("Email ID")
    st.write("shivacva20@gmail.com")
    st.subheader("Github")
    st.write("https://github.com/Shiva-kalyanaram")
    st.balloons()
