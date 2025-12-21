import argparse
import os
import csv
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

def calculate_area(image_path):
    """Вычисляет площадь изображения (width * height)."""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            return width * height
    except Exception as e:
        print(f"Ошибка при чтении {image_path}: {e}")
        return 0  

def get_area_range(area):
    """Определяет диапазон для площади (диапазоны подбираются динамически)."""
    if area == 0:
        return 'Invalid'
    elif area <= 100000:
        return '0-100000'
    elif area <= 200000:
        return '100001-200000'
    elif area <= 300000:
        return '200001-300000'
    elif area <= 400000:
        return '300001-400000'
    elif area <= 500000:
        return '400001-500000'
    else:
        return '500001+'

def sort_by_area_range(df):
    """Сортирует DataFrame по колонке 'area_range'."""
    return df.sort_values(by='area_range')

def filter_by_area_range(df, range_value):
    """Фильтрует DataFrame по конкретному значению в 'area_range'."""
    return df[df['area_range'] == range_value]

def main():
    parser = argparse.ArgumentParser(description="Обработка аннотации из второй лабы: DataFrame с путями, площадями и гистограммой.")
    parser.add_argument('--annotation_file', type=str, required=True, help="Путь к CSV-аннотации из второй лабы")
    parser.add_argument('--output_df', type=str, default='./processed_df.csv', help="Путь для сохранения DataFrame в CSV")
    parser.add_argument('--output_plot', type=str, default='./area_histogram.png', help="Путь для сохранения графика в PNG")

    args = parser.parse_args()

    if not os.path.isfile(args.annotation_file):
        raise FileNotFoundError(f"Аннотация не найдена: {args.annotation_file}")

    paths = []
    with open(args.annotation_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None) 
        for row in reader:
            if row:
                abs_path = row[0].strip()
                rel_path = os.path.relpath(abs_path)  # Относительный путь
                paths.append({'absolute_path': abs_path, 'relative_path': rel_path})

    df = pd.DataFrame(paths)

    df['image_area'] = df['absolute_path'].apply(calculate_area)

    df['area_range'] = df['image_area'].apply(get_area_range)

    print("Сформированный DataFrame:")
    print(df.head()) 

    sorted_df = sort_by_area_range(df)
    print("\nОтсортированный DataFrame по 'area_range':")
    print(sorted_df.head())

    if not sorted_df.empty:
        example_range = sorted_df['area_range'].iloc[0]
        filtered_df = filter_by_area_range(sorted_df, example_range)
        print(f"\nФильтрованный DataFrame по диапазону '{example_range}':")
        print(filtered_df)

    range_counts = sorted_df['area_range'].value_counts().sort_index() 
    plt.figure(figsize=(10, 6))
    range_counts.plot(kind='bar')
    plt.title('Гистограмма распределения площадей изображений по диапазонам')
    plt.xlabel('Диапазон площади (пикселей)')
    plt.ylabel('Количество изображений')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(args.output_plot)
    print(f"\nГрафик сохранён в: {args.output_plot}")
    plt.show()  

    df.to_csv(args.output_df, index=False, encoding='utf-8')
    print(f"DataFrame сохранён в: {args.output_df}")

if __name__ == '__main__':
    main()