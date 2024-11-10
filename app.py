import os
import requests
from flask import Flask, request, jsonify, send_file
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Configuração da Imagine API
IMAGINE_API_URL = "https://api.vyro.ai/v1/imagine/api/generations"
IMAGINE_API_BEARER = "vk-KmgntjQWQfnjTzbkQKViD0xY3bf0r478WVRwjv3tKzAaa"

def compress_to_webp(image_data):
    """
    Comprime a imagem para o formato WEBP com qualidade ajustada.
    """
    # Abrir a imagem a partir do conteúdo recebido
    image = Image.open(BytesIO(image_data))
    
    # Criar um objeto BytesIO para armazenar a imagem comprimida
    compressed_image_io = BytesIO()
    
    # Salvar a imagem no formato WEBP com compressão
    image.save(compressed_image_io, format="WEBP", quality=70, optimize=True)
    
    # Posicionar o ponteiro no início do buffer para leitura posterior
    compressed_image_io.seek(0)
    
    return compressed_image_io

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """
    Endpoint que gera uma imagem com a Imagine API, comprime para WEBP e retorna a imagem comprimida.
    """
    try:
        # 1. Ler os dados da requisição
        data = request.json
        prompt = data.get('prompt')
        filename = data.get('filename', 'compressed_image')  # Nome do arquivo padrão

        if not prompt:
            return jsonify({'error': 'O prompt é obrigatório.'}), 400

        # 2. Fazer a requisição para a Imagine API
        headers = {
            "Authorization": f"Bearer {IMAGINE_API_BEARER}"
        }
        payload = {
            "prompt": (None, prompt),  # Campos multipart/form-data
            "aspect_ratio": (None, "16:9"),
            "style_id": (None, "122")
        }
        response = requests.post(IMAGINE_API_URL, headers=headers, files=payload)

        # Verificar se a resposta foi bem-sucedida
        if response.status_code != 200:
            return jsonify({'error': f"Erro na Imagine API: {response.text}"}), response.status_code

        # Obter a imagem diretamente do corpo da resposta
        image_data = response.content

        # Verificar se o conteúdo da imagem está vazio
        if not image_data or len(image_data) == 0:
            return jsonify({'error': 'Erro: O conteúdo da imagem gerada está vazio.'}), 500

        # 3. Comprimir a imagem para WEBP
        compressed_image = compress_to_webp(image_data)

        # 4. Preparar o nome do arquivo para o retorno
        base_filename = os.path.splitext(filename)[0]  # Remove extensão existente, se houver
        output_filename = f"{base_filename}.webp"

        # 5. Retornar a imagem comprimida
        return send_file(
            compressed_image,
            mimetype="image/webp",
            download_name=output_filename,
            as_attachment=True
        )

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f"Erro ao fazer requisição HTTP: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Ocorreu um erro: {str(e)}"}), 500
