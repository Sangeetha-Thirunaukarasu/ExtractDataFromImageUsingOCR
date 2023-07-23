import base64

import streamlit as st  # for GUI development
import easyocr  # ocr engine to extract data from the image  b
import pandas as pd
import numpy as np
import os
# import cv2
# import re
# importing required modules for db connection
import mysql.connector
import pymysql
import sqlalchemy as sal
from sqlalchemy import text

st.title("Extract Business Card Data - OCR")

host = 'localhost'
user = 'root'
pw = 'root'
db_name = 'DB_OCR'
port = '3306'


def db_connection():  # connect mysql db
    eng = sal.create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}'.format(
        user=user, password=pw, host=host, port=port, db_name=db_name))
    return eng.connect()


def create_db():   # create database
    eng = db_connection()
    # conx.execute(text('CREATE DATABASE DATA_OCR'))
    eng.execute(text("show databases"))


def db_table_create():   # create table
    eng = db_connection()
    #eng.close()
    # conx.execute(text('CREATE DATABASE DATA_OCR'))
    eng.execute(text('CREATE TABLE OCR_DATA_TABLE('
                     'ID INT AUTO_INCREMENT PRIMARY KEY,'
                     'COMPANY_NAME VARCHAR(50),'
                     'CARD_HOLDER_NAME VARCHAR(50),'
                     'DESIGNATION VARCHAR(20),'
                     'MOBILE_NUM VARCHAR(20),'
                     'OFFICE_NUMBER VARCHAR(15),'
                     'EMAIL_ADDRESS1 VARCHAR(20),'
                     'EMAIL_ADDRESS2 VARCHAR(20),'
                     'WEBSITE_URL VARCHAR(20),'
                     'AREA VARCHAR(20),'
                     'CITY VARCHAR(20),'
                     'STATE VARCHAR(20),'
                     'PINCODE INT(6))'))
    return st.success("Table created")


tab1, tab2, tab3 = st.tabs(['Add NEW', 'View and Update', 'Delete'])


with tab1:
    def img_uploader():   # image uploader
        st.subheader('**:blue[Upload your Business Card]**')
        up_img = st.file_uploader(label='Upload an image', key='image', type=['jpg', 'png', 'jpeg'])
        return up_img

    # saving the image in folder
    def save_dir(sa_img):
        with open(os.path.join("", sa_img.name), 'wb') as f:
            f.write(sa_img.getbuffer())
            # return st.success('saved')


    get_img = img_uploader()
    if get_img:
        img_det = {'File name': get_img.name, 'File type': get_img.type}
        # st.write(img_det)
        save_dir(get_img)

    # Image preprocesing - image resizing before fed into OCR engine
    # reading the imagesdcx
    # def img_prepro(img_pro):
    #     img = cv2.imread(img_pro.name)
    #     img1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #     # OTSU thresholding + binary thresholding
    #     ret, thresh = cv2.threshold(img1, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
    #     (height, width) = thresh.shape[:2]
    #     res = cv2.resize(thresh, (int(width / 2), int(height / 2)), interpolation=cv2.INTER_AREA)
    #     cv2.imwrite('copy.png', res)

    # def img_pre_pro(pro_img):
    #     # read the image
    #     img = cv2.imread(pro_img.name)
    #     # st.write(type(img)) # o/p=>numpy array
    #     # converting into greyscale
    #     img1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #     # thresholding -  OTSU
    #     ret, thresh = cv2.threshold(img1, 0, 255, cv2.THRESH_OTSU+cv2.THRESH_BINARY)
    #
    #     # specify the structure shape and kernel size
    #     rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 30))
    #
    #     # apply the dilation on the threshold image
    #     dil = cv2.dilate(thresh, rect_kernel, iterations=1)
    #
    #     contours, hierarchy = cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #
    #     # get the no.of pixels horizontally and vertically(tuple unpacking)
    #     # from obj shape(rows,col,channels)
    #     # (height, width) = img.shape[:2]
    #
    #     # INTERPOLATION = inter_cubic --> for zooming(for 2 dim regular grid)
    #     # res = cv2.resize(thresh, (int(width/2), int(height/2)), interpolation=cv2.INTER_AREA)
    #     for cont in contours:
    #         x, y, w, h = cv2.boundingRect(cont)
    #         rect = cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    #         cropped = img[y:y+h, x:x+w]
    #         reader1 = easyocr.Reader(['en'])
    #         res1 = reader.readtext(cropped, detail=0, paragraph=True)
    #         # new_res = np.array(res).reshape(1,-1)
    #         # st.write((np.array(res).shape)[0])
    #         # st.write(res)
    #         return res1

    # initialising session state
    if 'data_edit' not in st.session_state:
        st.session_state['data_edit'] = 0

    # converting image file to binary format
    def image_to_bin():
        file = open(get_img.name, 'rb').read()
        img_file = base64.b64encode(file)
        # with open(get_img.name, 'rb') as file:
        #     binary_data = file.read()
        return img_file

    def call_back():
        st.session_state['data_edit'] += 1

    def ocr_reader():
        # img_prepro(get_img)
        reader = easyocr.Reader(['en'])
        res = reader.readtext(get_img.name, detail=0, paragraph=False)
        res = [val.lower() for val in res]
        if len(res) < 12:
            for j in range(0, 12-len(res)):
                res.append('')
        # convert the image to binary data
        img_data = image_to_bin()
        # append the original image to the extracted list
        res.append(img_data)
        #st.write(res)
        # reshaping the rows to columns
        new_res = np.array(res).reshape(1, -1)
        # st.write(np.array(res).shape[0])
        # st.write(new_res)
        # st.write(new_res.shape[1])
        st.write("**:green[The extracted information are:]**")
        # convert list into data frame
        db_data = pd.DataFrame(new_res, columns=(['CARD_HOLDER_NAME', 'DESIGNATION', 'MOBILE_NUM', 'OFFICE_NUMBER',
                                                  'EMAIL_ADDRESS1', 'EMAIL_ADDRESS2', 'WEBSITE_URL', 'AREA', 'CITY',
                                                  'STATE', 'PINCODE', 'COMPANY_NAME', 'IMAGE']))
        # Editable dataframe
        final_data = st.data_editor(db_data, key='data_editor', on_change=call_back(), hide_index=True, use_container_width=True)
        save = st.button('Save', key='save')
        st.write("**:red[kindly check all the field has correct values before save]")
        if save:
            connection = db_connection()
            # final_data--> dataframe,
            # OCR_DATA_TABLE-->SQL table
            # using to_sql method in DF, converting and insert df to sql table
            final_data.to_sql(con=connection, name='ocr_data_table', if_exists='append', index=False)
            connection.close()
            st.success("Saved Successfully")

    # ocr_reader()

    try:
        ocr_reader()
    except BaseException as e:
        pass

with tab2:
    st.write("**Please enter your registered name and designation and press 'Enter'**")
    name = st.text_input('Enter your name ', key='name1')
    design = st.text_input('Enter your Designation ', key='design1')
    #if st.button('View Data', key='view1'):
    if name != "" and design != "":
        #try:
        con = db_connection()
        # data1 = conn.execute(text('select COMPANY_NAME, CARD_HOLDER_NAME, DESIGNATION, MOBILE_NUM,OFFICE_NUMBER, EMAIL_ADDRESS1, EMAIL_ADDRESS2, WEBSITE_URL, AREA, CITY, STATE, PINCODE from ocr_data_table where CARD_HOLDER_NAME="' + name + '" and DESIGNATION="' + design + '"'))
        query = 'select * from ocr_data_table where CARD_HOLDER_NAME="' + name.casefold() + '" and DESIGNATION="' + design.casefold() + '"'
        retrie = con.execute(text(query))
        ret = list(retrie)
        #st.write(ret)
        if ret:
            st.write("The retrieved information given below:")
            col_list = ['ID', 'COMPANY_NAME', 'CARD_HOLDER_NAME', 'DESIGNATION', 'MOBILE_NUM', 'OFFICE_NUMBER', 'EMAIL_ADDRESS1',
                        'EMAIL_ADDRESS2', 'WEBSITE_URL', 'AREA', 'CITY', 'STATE', 'PINCODE']
            with st.form('my_form'):
                for da in range(1, len(col_list)):
                    col_list[da] = st.text_input(label=col_list[da], value=ret[0][da], key=col_list[da])
                submitted = st.form_submit_button('Save')
                if submitted:
                    col_list1 = ['ID', 'COMPANY_NAME', 'CARD_HOLDER_NAME', 'DESIGNATION', 'MOBILE_NUM', 'OFFICE_NUMBER',
                                 'EMAIL_ADDRESS1', 'EMAIL_ADDRESS2', 'WEBSITE_URL', 'AREA', 'CITY', 'STATE', 'PINCODE']
                    for col in range(1, len(col_list)):
                        query_up = 'update ocr_data_table set ' + col_list1[col]+' = ' + '"' + col_list[col] + '"' + ' where ID = {}'.format(ret[0][0])
                        # st.write(query_up)
                        con.execute(text(query_up))
                    st.success("Updated successfully")
                    con.close()
        else:
            st.error("Name or Designation is not registered")
        #except BaseException as e:
         #   st.write(e)
        #else:
         #   st.warning("Please fill all the fields")

with tab3:
    if 'new_df' not in st.session_state:
        st.session_state.new_df = 0


    # if 'view' not in st.session_state:
    # st.session_state['view'] = 0

    def callback1():
        st.session_state['new_df'] += 1


    # def view_button():
    # st.session_state.view = 1

    name = st.text_input('Enter your name ', key='name')
    design = st.text_input('Enter your Designation ', key='design')
    view = st.button('View Data', key='view')

    if view:
        con = db_connection()
        data = 'select COMPANY_NAME, CARD_HOLDER_NAME, DESIGNATION, MOBILE_NUM,OFFICE_NUMBER, EMAIL_ADDRESS1, EMAIL_ADDRESS2, WEBSITE_URL, AREA, CITY, STATE, PINCODE from ocr_data_table where CARD_HOLDER_NAME="' + name + '" and DESIGNATION="' + design + '"'
        df1 = pd.read_sql(data, con=con)
        st.write(data)
        # new_df = st.data_editor(df1, num_rows='dynamic', key='new_df') #on_change=callback1())

        st.button('Save Changes', key='save_change')

    #df = pd.read_sql(query, conn)
    # d1 = dict(df)
    # new_dat = st.data_editor(df, hide_index=True)
    # # st.write(type(new_dat))
    # d2 = dict(new_dat)
    # # st.write(d)
    # lis = ['COMPANY_NAME', 'CARD_HOLDER_NAME', 'DESIGNATION', 'MOBILE_NUM', 'OFFICE_NUMBER', 'EMAIL_ADDRESS1',
    #        'EMAIL_ADDRESS2', 'WEBSITE_URL', 'AREA', 'CITY', 'STATE', 'PINCODE']
    # for i in lis:
    #     query = f'update ocr_data_table set {i} = "{d2[i].values[0]}" where ID = {d2["ID"].values[0]}'
    #     #st.write(query)
    #     conn.execute(text(query))
    # st.success('updated successfully')
