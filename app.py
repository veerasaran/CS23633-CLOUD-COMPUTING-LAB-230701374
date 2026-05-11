from flask import Flask, request, render_template
import os
import time
import subprocess
from caption import generate_caption
from model import detect_objects

app = Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']

        if file:
            # Remove old images
            for f in ["input.jpg", "output.jpg"]:
                path = os.path.join(UPLOAD_FOLDER, f)

                if os.path.exists(path):
                    os.remove(path)

            input_path = os.path.join(UPLOAD_FOLDER, "input.jpg")
            file.save(input_path)

            objects, output_image, object_names = detect_objects(input_path)

            caption = generate_caption(input_path)

            # Simple explanation
            explanation = caption.capitalize()

            # Prevent browser caching
            output_image = output_image + "?t=" + str(time.time())

            return render_template(
                'index.html',
                image=output_image,
                objects=objects,
                explanation=explanation,
                message=None
            )

    return render_template('index.html', message=None)


@app.route('/webcam')
def webcam():
    import threading
    import webcam

    # NOTE:
    # This route works locally only.
    # Webcam/OpenCV window will NOT work on Azure Web App.

    threading.Thread(target=webcam.run, daemon=True).start()

    return "🎥 Webcam started! Check the OpenCV window. Press Q to exit."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)