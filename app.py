import os
import requests
from flask import Flask, request, jsonify, send_file
from PIL import Image
from io import BytesIO

app = Flask(__name__)

IMAGINE_API_URL = "https://api.vyro.ai/v1/imagine/api/generations"
IMAGINE_API_BEARER = "vk-KmgntjQWQfnjTzbkQKViD0xY3bf0r478WVRwjv3tKzAaa"

def compress_and_convert_image(image_data):
    """
    Comprime e converte a imagem para o formato WEBP.
    """
    image = Image.open(BytesIO(image_data))

    # Crie um objeto BytesIO para salvar a imagem comprimida
    compressed_image_io = BytesIO()
    image.save(compressed_image_io, format="WEBP", quality=70, optimize=True)
    compressed_image_io.seek(0)

    return compressed_image_io


@app.route('/generate-and-compress', methods=['POST'])
def generate_and_compress():
    """
    Endpoint que gera uma imagem com a Imagine API a partir de um prompt,
    comprime a imagem em formato WEBP e retorna o arquivo.
    """
    data = request.json
    prompt = data.get('prompt')
    filename = data.get('filename', 'compressed_image')  # Nome do arquivo opcional

    if not prompt:
        return jsonify({'error': 'O prompt é obrigatório.'}), 400

    try:
        # 1. Fazer requisição para a Imagine API
        headers = {
            "Authorization": f"Bearer {IMAGINE_API_BEARER}"
        }
        payload = {
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "style_id": 122
        }
        response = requests.post(IMAGINE_API_URL, headers=headers, data=payload)

        if response.status_code != 200:
            return jsonify({'error': f"Erro na Imagine API: {response.text}"}), response.status_code

        # Obter a URL da imagem gerada
        image_url = response.json().get("image_url")
        if not image_url:
            return jsonify({'error': 'Não foi possível obter a URL da imagem gerada.'}), 500

        # 2. Fazer download da imagem gerada
        image_response = requests.get(image_url, stream=True)
        image_response.raise_for_status()  # Verifica se houve algum erro na requisição
        image_data = image_response.content

        # 3. Comprimir e converter a imagem
        compressed_image = compress_and_convert_image(image_data)

        # 4. Preparar o nome do arquivo para o retorno
        base_filename = os.path.splitext(filename)[0]  # Remover extensão existente (se houver)
        output_filename = f"{base_filename}.webp"

        # 5. Retornar a imagem comprimida
        return send_file(
            compressed_image,
            mimetype="image/webp",
            download_name=output_filename,
            as_attachment=True
        )

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Erro ao baixar a imagem: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Ocorreu um erro: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
