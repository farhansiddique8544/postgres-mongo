from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from  werkzeug.utils import secure_filename 
import psycopg2 #pip install psycopg2 
import psycopg2.extras 



IMAGE_UP= os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__)
     
app.secret_key = "cairocoders-ednalan"
     
DB_HOST = "localhost"
DB_NAME = "image_embeddings"
DB_USER = "postgres"
DB_PASS = "gysim#234"
     
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
  
IMAGE_UP = 'downloads/python'
  
app.secret_key = "secret key"
app.config['IMAGE_UP'] = IMAGE_UP
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
  
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
  
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
      
  
@app.route('/')
def home():
    return render_template('index.html')
  
@app.route('/', methods=['POST'])
def upload_image():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
        zip_img=zipfile.ZipFile(os.path.join(IMAGE_UP, filename), 'r')
        zip_img.extractall(IMAGE_UP)
        zip_img.close()
        images_folder = os.path.join(IMAGE_UP, 'test')  # the folder where the extracted images are stored
        images = os.listdir(images_folder)  # list all the files in the folder
        if len(images) > 0:  # if there is at least one image file
          image_path = os.path.join(images_folder, images[0])

        embedding = get_embeddings(image_path)
        img_name = image_path.split('\\')[-1]
        cursor.execute("INSERT INTO upload (title,embedding, name) VALUES (%s,%s,%s)", (image_path, str(embedding), img_name))
        conn.commit()

        return render_template('index.html', image_path=image_path)
    
 
        # flash('Image successfully uploaded and displayed below')
        # return render_template('index.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)
  
@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('downloads', filename='python/' + filename), code=301)
  
if __name__ == "__main__":
    app.run()