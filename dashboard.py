# Modules
import pyrebase
import streamlit as st
import pandas as pd
from datetime import datetime
# for menu
from streamlit_option_menu import option_menu
# aggrid
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder


# Configuration Key
firebaseConfig = {
    'apiKey': "AIzaSyDd0pyh3QtdRevImwmxoaXXIJJnl0sQgYM",
    'authDomain': "newfc0.firebaseapp.com",
    'projectId': "newfc0",
    'databaseURL': "https://newfc0-default-rtdb.firebaseio.com/",
    'storageBucket': "newfc0.appspot.com",
    'messagingSenderId': "902883678033",
    'appId': "1:902883678033:web:3f6f72f2ee492d4d1a2570",
    'measurementId': "G-RR3MCH8Y5Z"
}

#   apiKey: "AIzaSyDd0pyh3QtdRevImwmxoaXXIJJnl0sQgYM",
#   authDomain: "newfc0.firebaseapp.com",
#   projectId: "newfc0",
#   storageBucket: "newfc0.appspot.com",
#   messagingSenderId: "902883678033",
#   appId: "1:902883678033:web:3f6f72f2ee492d4d1a2570",
#   measurementId: "G-RR3MCH8Y5Z"


st.sidebar.image(
    "https://assets.website-files.com/5d5e2ff58f10c53dcffd8683/5d5e30797662017855f689a6_unboxing.svg", use_column_width=True)


# Firebase Authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Database
db = firebase.database()
storage = firebase.storage()
st.sidebar.title("NewFCo")

# Authentication
choice = st.sidebar.selectbox('login/Signup', ['Login', 'Sign up'])

# Obtain User Input for email and password
email = st.sidebar.text_input('Please enter your email address')
password = st.sidebar.text_input('Please enter your password', type='password')

# App

# Main menu
selected = option_menu(
    menu_title=None,  # required
    options=["Home", "Products", "Notification", "Setting"],  # required
    icons=["house", "book", "envelope"],  # optional
    menu_icon="cast",  # optional
    default_index=0,  # optional
    orientation="horizontal",
)
# return selected

if selected == "Home":
    st.title(f"You have selected {selected}")
if selected == "Products":
    # Load data
    @st.cache
    def data_upload():
        url = "https://people.sc.fsu.edu/~jburkardt/data/csv/taxables.csv"
        df = pd.read_csv(url, error_bad_lines=False)
        return df
    st.subheader("Data")
    df = data_upload()

    st.title(f"You have selected {selected}")
    gd = GridOptionsBuilder.from_dataframe(df)
    gd.configure_selection(selection_mode='multiple', use_checkbox=True)
    gd.configure_default_column(editable=True, groupable=True)
    gd.configure_pagination(enabled=True)
    gridoptions = gd.build()
    grid1 = AgGrid(df, gridOptions=gridoptions,
                   update_mode=GridUpdateMode.SELECTION_CHANGED)

    sel_row = grid1["selected_rows"]  # Type -> List
    df_sel = pd.DataFrame(sel_row)  # Convert list to dataframe
    st.subheader("Output")

if selected == "Notification":
    st.title(f"You have selected {selected}")
if selected == "Setting":
    st.title(f"You have selected {selected}")


# menu ends


# Sign up Block
if choice == 'Sign up':
    handle = st.sidebar.text_input(
        'Please input your app handle name', value='Default')
    submit = st.sidebar.button('Create my account')

    if submit:
        user = auth.create_user_with_email_and_password(email, password)
        st.success('Your account is created suceesfully!')
        st.balloons()
        # Sign in
        user = auth.sign_in_with_email_and_password(email, password)
        db.child(user['localId']).child("Handle").set(handle)
        db.child(user['localId']).child("ID").set(user['localId'])
        st.title('Welcome' + handle)
        st.info('Login via login drop down selection')

# Login Block
if choice == 'Login':
    login = st.sidebar.checkbox('Login')
    if login:
        user = auth.sign_in_with_email_and_password(email, password)
        st.write(
            '<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        bio = st.radio('Jump to', ['Home', 'Workplace Feeds', 'Settings'])

# SETTINGS PAGE
        if bio == 'Settings':
            # CHECK FOR IMAGE
            nImage = db.child(user['localId']).child("Image").get().val()
            # IMAGE FOUND
            if nImage is not None:
                # We plan to store all our image under the child image
                Image = db.child(user['localId']).child("Image").get()
                for img in Image.each():
                    img_choice = img.val()
                    # st.write(img_choice)
                st.image(img_choice)
                exp = st.beta_expander('Change Bio and Image')
                # User plan to change profile picture
                with exp:
                    newImgPath = st.text_input(
                        'Enter full path of your profile imgae')
                    upload_new = st.button('Upload')
                    if upload_new:
                        uid = user['localId']
                        fireb_upload = storage.child(uid).put(
                            newImgPath, user['idToken'])
                        a_imgdata_url = storage.child(uid).get_url(
                            fireb_upload['downloadTokens'])
                        db.child(user['localId']).child(
                            "Image").push(a_imgdata_url)
                        st.success('Success!')
            # IF THERE IS NO IMAGE
            else:
                st.info("No profile picture yet")
                newImgPath = st.text_input(
                    'Enter full path of your profile image')
                upload_new = st.button('Upload')
                if upload_new:
                    uid = user['localId']
                    # Stored Initated Bucket in Firebase
                    fireb_upload = storage.child(uid).put(
                        newImgPath, user['idToken'])
                    # Get the url for easy access
                    a_imgdata_url = storage.child(uid).get_url(
                        fireb_upload['downloadTokens'])
                    # Put it in our real time database
                    db.child(user['localId']).child(
                        "Image").push(a_imgdata_url)
 # HOME PAGE
        elif bio == 'Home':
            col1, col2 = st.beta_columns(2)

            # col for Profile picture
            with col1:
                nImage = db.child(user['localId']).child("Image").get().val()
                if nImage is not None:
                    val = db.child(user['localId']).child("Image").get()
                    for img in val.each():
                        img_choice = img.val()
                    st.image(img_choice, use_column_width=True)
                else:
                    st.info(
                        "No profile picture yet. Go to Edit Profile and choose one!")

                post = st.text_input(
                    "Let's share my current mood as a post!", max_chars=100)
                add_post = st.button('Share Posts')
            if add_post:
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                post = {'Post:': post,
                        'Timestamp': dt_string}
                results = db.child(user['localId']).child("Posts").push(post)
                st.balloons()

            # This coloumn for the post Display
            with col2:

                all_posts = db.child(user['localId']).child("Posts").get()
                if all_posts.val() is not None:
                    for Posts in reversed(all_posts.each()):
                        # st.write(Posts.key()) # Morty
                        st.code(Posts.val(), language='')
   # WORKPLACE FEED PAGE
        else:
            all_users = db.get()
            res = []
            # Store all the users handle name
            for users_handle in all_users.each():
                k = users_handle.val()["Handle"]
                res.append(k)
            # Total users
            nl = len(res)
            st.write('Total users here: ' + str(nl))

            # Allow the user to choose which other user he/she wants to see
            choice = st.selectbox('My Collegues', res)
            push = st.button('Show Profile')

            # Show the choosen Profile
            if push:
                for users_handle in all_users.each():
                    k = users_handle.val()["Handle"]
                    #
                    if k == choice:
                        lid = users_handle.val()["ID"]

                        handlename = db.child(lid).child("Handle").get().val()

                        st.markdown(handlename, unsafe_allow_html=True)

                        nImage = db.child(lid).child("Image").get().val()
                        if nImage is not None:
                            val = db.child(lid).child("Image").get()
                            for img in val.each():
                                img_choice = img.val()
                                st.image(img_choice)
                        else:
                            st.info(
                                "No profile picture yet. Go to Edit Profile and choose one!")

                        # All posts
                        all_posts = db.child(lid).child("Posts").get()
                        if all_posts.val() is not None:
                            for Posts in reversed(all_posts.each()):
                                st.code(Posts.val(), language='')
