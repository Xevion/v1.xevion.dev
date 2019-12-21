from app import app
from textwrap import wrap
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import flask

@app.route('/panzer/')
@app.route('/panzer')
@app.route('/panzer/<string>')
@app.route('/panzer/<string>/')
def panzer(string='bionicles are cooler than sex'):
    string = string.replace('+', ' ')
    string = string.replace('\n', '%0A')
    image = create_panzer(string)
    return serve_pil_image(image)

def create_panzer(string):
    img = Image.open("./app/static/panzer.jpeg")
    draw = ImageDraw.Draw(img)
    font1 = ImageFont.truetype('./app/static/arial.ttf', size=30)
    draw.text((10, 20), 'Oh panzer of the lake, what is your wisdom?', font=font1)
    font2 = ImageFont.truetype('./app/static/arial.ttf', size=30)
    topleft = (250, 500)
    wrapped = wrap(string, width=25)
    wrapped = [text.replace('%0A', '\n') for text in wrapped]
    for y, text in enumerate(wrapped):
        draw.text((topleft[0], topleft[1] + (y * 33)), text, font=font2)
    return img

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=50)
    img_io.seek(0)
    return flask.send_file(img_io, mimetype='image/jpeg')  