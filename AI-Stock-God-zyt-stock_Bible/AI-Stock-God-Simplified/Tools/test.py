
import base64

def image(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        print(encoded_string)
    return encoded_string
if __name__ == "__main__":
    image_path = r'C:\Users\zddydy\Desktop\KlineCharts\price_chart.png'
    encoded_string = image(image_path)