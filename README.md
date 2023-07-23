# ExtractDataFromImageUsingOCR
# about:
a Streamlit application that allows users to
upload an image of a business card and extract relevant information from it using
easyOCR.

# Tools Required:
python 3.11.2
numpy 
streamlit 1.24.1
easyOCR
MySql(sqlalchemy +pymongo)
opencv(cv2)

# flow of execution:
developed the GUI part using Streamlit
a file uploader is to uplaod the image of a business card
Image file is getting stored in the directory once the file is successfully uplaoded
before the sned the image file to ocr engine, the image preprocessing takes place like, image resizing, thresholding to enhance the quality of the image.
The uploaded file is fed into easyOCR engine which recognize the text present in the image file.
the extracted information then converted into dataframe.
and then display the data from dataframe as editable data table in the application's GUI
user can check the information and easliy change the values if needed. then save the data into db by clicking save button
the db connecions are made using sqlalchemy and pymysql. using to_sql function, the data are getting inserted along with binary form of an image into DB successfully.
user can view the data and delete the records from db.

# conclusion:
This is the application which is helpful for businesses and individuals to store and manage multiple business card information
 



