import base64


def get_words():
    files = []
    with open('data/generated_text.txt', 'r') as file:
        for line in file:
            filename = line.strip()
            base64_content = base64.b64encode(filename.encode('utf-8')).decode('utf-8')
            data_url = f'data:text/plain;charset=utf-8;base64,{base64_content}'
            files.append({
                'filename': filename,
                'dataURL': data_url
            })
    return files
