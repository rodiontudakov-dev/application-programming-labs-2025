import argparse
import os
from PIL import Image
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description="Обработка изображения: поворот на заданный угол.")
    parser.add_argument('--input_file', type=str, required=True, help="Путь к исходному файлу изображения (из предыдущей лабы)")
    parser.add_argument('--output_file', type=str, required=True, help="Путь для сохранения результата")
    parser.add_argument('--angle', type=float, default=90.0, help="Угол поворота в градусах (по умолчанию 90)")

    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        raise FileNotFoundError(f"Исходный файл не найден: {args.input_file}")

    img = Image.open(args.input_file)

    width, height = img.size
    print(f"Размер исходного изображения: {width} x {height} пикселей")

    rotated_img = img.rotate(args.angle, expand=True)

    rotated_img.save(args.output_file)
    print(f"Повернутое изображение сохранено в: {args.output_file}")

    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    
    axs[0].imshow(img)
    axs[0].set_title('Исходное изображение')
    axs[0].axis('off')
    
    axs[1].imshow(rotated_img)
    axs[1].set_title(f'Повернутое на {args.angle}°')
    axs[1].axis('off')
    
    plt.show()  

if __name__ == '__main__':
    main()