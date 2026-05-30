from flask import Flask, request, send_file, jsonify, after_this_request
from flask_cors import CORS
import os
import subprocess
import uuid

app = Flask(__name__)
CORS(app)

GS = "gs"

@app.route("/compress", methods=["POST"])
def compress_pdf():

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    quality = request.form.get("quality", "ebook")

    input_path = f"/tmp/{uuid.uuid4()}_in.pdf"
    output_path = f"/tmp/{uuid.uuid4()}_out.pdf"

    file.save(input_path)

    try:
        subprocess.check_output([
            GS,
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            f'-dPDFSETTINGS=/{quality}',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-sOutputFile={output_path}',
            input_path
        ])

        @after_this_request
        def cleanup(response):
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
            except Exception:
                pass
            return response

        return send_file(
            output_path,
            as_attachment=True,
            download_name="compressed.pdf"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
