import argparse
import os
import csv
from icrawler.builtin import BingImageCrawler


class ImagePathIterator:
    """
    Итератор по путям к файлам изображений.
    Конструктор принимает либо путь к CSV-аннотации, либо путь к папке с изображениями.
    При чтении из CSV возвращает абсолютный путь (поле 'absolute_path').
    """
    def __init__(self, path):
        self.paths = []
        if os.path.isfile(path):
            with open(path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader, None)
                if header and 'absolute_path' in header:
                    abs_idx = header.index('absolute_path')
                else:
                    abs_idx = 0  
                for row in reader:
                    if row:
                        self.paths.append(row[abs_idx].strip())
        elif os.path.isdir(path):
            self.paths = [
                os.path.abspath(os.path.join(path, f))
                for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))
            ]
        else:
            raise ValueError("Указанный путь не является файлом или директорией.")
        
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.paths):
            path = self.paths[self.index]
            self.index += 1
            return path
        raise StopIteration


def main():
    parser = argparse.ArgumentParser(description="Скачивание полутоновых изображений с Bing, создание аннотации CSV (с абсолютным и относительным путями) и итератор по путям.")
    parser.add_argument('--keyword', type=str, default='dog', help="Ключевое слово для поиска (по умолчанию 'dog')")
    parser.add_argument('--save_dir', type=str, required=True, help="Папка для сохранения изображений")
    parser.add_argument('--annotation_file', type=str, required=True, help="Путь к файлу аннотации CSV")
    parser.add_argument('--min_num', type=int, default=50, help="Минимальное количество изображений (по умолчанию 50)")
    parser.add_argument('--max_num', type=int, default=1000, help="Максимальное количество изображений (по умолчанию 1000)")

    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)

    filters = dict(
        color='blackandwhite',   
        type='photo'             
    )

    crawler = BingImageCrawler(storage={'root_dir': args.save_dir})
    
    crawler.crawl(
        keyword=args.keyword + ' black and white',
        filters=filters,
        max_num=args.max_num,
        min_size=(200, 200)
    )

    image_files = [
        f for f in os.listdir(args.save_dir)
        if os.path.isfile(os.path.join(args.save_dir, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]

    image_paths = []
    for filename in image_files:
        abs_path = os.path.abspath(os.path.join(args.save_dir, filename))
        rel_path = os.path.relpath(abs_path, start=os.path.dirname(os.path.abspath(args.save_dir)))
        image_paths.append((abs_path, rel_path if rel_path != '.' + os.sep + filename else filename))

    if len(image_paths) < args.min_num:
        print(f"Предупреждение: Скачано только {len(image_paths)} изображений, меньше минимального {args.min_num}")

    with open(args.annotation_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['absolute_path', 'relative_path']) 
        for abs_path, rel_path in image_paths:
            writer.writerow([abs_path, rel_path])

    print(f"Скачано {len(image_paths)} изображений в папку: {args.save_dir}")
    print(f"Аннотация (с абсолютными и относительными путями) сохранена в файл: {args.annotation_file}")

    print("\nПервые 5 записей из CSV (абсолютный и относительный пути):")
    with open(args.annotation_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        print(header)
        for i, row in enumerate(reader):
            if i < 5:
                print(row)
            else:
                break

    print("\nПервые 5 абсолютных путей через ImagePathIterator (из CSV):")
    iterator_csv = ImagePathIterator(args.annotation_file)
    for i, path in enumerate(iterator_csv):
        if i < 5:
            print(path)
        else:
            break

    print("\nПервые 5 абсолютных путей через ImagePathIterator (из папки):")
    iterator_dir = ImagePathIterator(args.save_dir)
    for i, path in enumerate(iterator_dir):
        if i < 5:
            print(path)
        else:
            break


if __name__ == '__main__':
    main()