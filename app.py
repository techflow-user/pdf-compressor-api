from flask import Flask, request, send_file, jsonify
import os
import subprocess
import uuid

app = Flask(__name__)

GS = "gs"  # su Linux hosting

@app.route("/compress", methods=["POST"])
def compress_pdf():
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

        size_in = os.path.getsize(input_path)
        size_out = os.path.getsize(output_path)

        reduction = (1 - size_out/size_in) * 100

        return send_file(
            output_path,
            as_attachment=True,
            download_name="compressed.pdf"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    app.run(debug=True)