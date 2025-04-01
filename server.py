import chevron
import mariadb
from flask import Flask, request, session, Response

# read all pages into a dictionary, key = page name, value = page content
pages = {}
for page_name in ['dashboard', 'home', 'error']:
    with open(f'pages/{page_name}.html') as f:
        pages[page_name] = f.read()
# read all images into a dictionary, key = image name, value = image content
images = {}
for image_name in ['smiley']:
    # read the image file in binary mode, r=read, b=binary
    with open(f'images/{image_name}.png', 'rb') as f:
        images[image_name] = f.read()

app = Flask(__name__)
app.secret_key = 'unique_secret_key'
connection_parameters = {
    "user": "student2025",
    "password": "1234",
    "host": "www.digilearn.be",
    "port": 33306,
    "database": "basics"
}


@app.route('/')
def index():
    return pages['home']


@app.route('/login', methods=['POST'])
def login():
    # The "request" IS the http request, it contains the data sent by the client as the body of the request
    data = request.form
    username = data['username']
    password = data['password']
    with mariadb.connect(**connection_parameters) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT username, password FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            # The "session" object is a dictionary-like object that stores data forever, across requests
            # Store the username in the session if the login is successful
            if result is None or result[1] != password:
                return chevron.render(pages['error'], {'message': 'Invalid username or password'})
            else:
                session['username'] = username
                return chevron.render(pages['dashboard'], {'user': username})


@app.route('/logout')
def logout():
    session['username'] = None
    return pages['home']


@app.route('/image/<image_name>')
def get_image(image_name: str):
    if image_name not in images:
        return chevron.render(pages['error'], {'message': 'Image not found'})
    return Response(images[image_name], mimetype='image/png')


app.run(host='0.0.0.0', port=5000)
