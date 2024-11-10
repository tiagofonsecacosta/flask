import os
import requests
from flask import Flask, request, jsonify, send_file
from io import BytesIO

app = Flask(__name__)

# Configuração da Imagine API
IMAGINE_API_URL = "https://api.vyro.ai/v1/imagine/api/generations"
IMAGINE_API_BEARER = "vk-KmgntjQWQfnjTzbkQKViD0xY3bf0r478WVRwjv3tKzAaa"

@app.route('/generate-image', methods=['POST'])
def generate_image():
    """
    Endpoint que gera uma imagem com a Imagine API a partir de um prompt e retorna a imagem em PNG.
    """
    logs = []  # Lista para armazenar os logs

    try:
        # 1. Ler os dados da requisição
        logs.append("Iniciando a leitura dos dados da requisição...")
        data = request.json
        prompt = data.get('prompt')
        filename = data.get('filename', 'generated_image')  # Nome do arquivo padrão

        if not prompt:
            logs.append("Erro: O prompt é obrigatório!")
            return jsonify({'error': 'O prompt é obrigatório.', 'logs': logs}), 400

        # 2. Fazer a requisição para a Imagine API
        logs.append(f"Preparando a requisição para a Imagine API com o prompt: {prompt}")
        headers = {
            "Authorization": f"Bearer {IMAGINE_API_BEARER}"
        }
        payload = {
            "prompt": (None, prompt),  # Campos multipart/form-data
            "aspect_ratio": (None, "16:9"),
            "style_id": (None, "122")
        }

        logs.append("Enviando requisição para a Imagine API...")
        response = requests.post(IMAGINE_API_URL, headers=headers, files=payload)

        # Verificar se a resposta foi bem-sucedida
        if response.status_code != 200:
            logs.append(f"Erro na Imagine API. Status code: {response.status_code}. Resposta: {response.text}")
            return jsonify({'error': f"Erro na Imagine API: {response.text}", 'logs': logs}), response.status_code

        logs.append("Requisição para a Imagine API foi bem-sucedida. Processando imagem...")

        # 3. Obter a imagem diretamente do corpo da resposta
        image_data = response.content

        # Verificar se o conteúdo da imagem está vazio
        if not image_data or len(image_data) == 0:
            logs.append("Erro: O conteúdo da imagem gerada está vazio.")
            return jsonify({'error': 'Erro: O conteúdo da imagem gerada está vazio.', 'logs': logs}), 500

        logs.append("Imagem gerada com sucesso pela Imagine API.")

        # 4. Preparar o nome do arquivo para o retorno
        base_filename = os.path.splitext(filename)[0]  # Remove extensão existente, se houver
        output_filename = f"{base_filename}.png"

        logs.append(f"Retornando a imagem gerada com o nome: {output_filename}")

        # 5. Retornar a imagem gerada
        return send_file(
            BytesIO(image_data),
            mimetype="image/png",
            download_name=output_filename,
            as_attachment=True
        )

    except requests.exceptions.RequestException as e:
        logs.append(f"Erro ao fazer requisição HTTP: {str(e)}")
        return jsonify({'error': f"Erro ao fazer requisição HTTP: {str(e)}", 'logs': logs}), 500
    except Exception as e:
        logs.append(f"Erro inesperado: {str(e)}")
        return jsonify({'error': f"Ocorreu um erro: {str(e)}", 'logs': logs}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
