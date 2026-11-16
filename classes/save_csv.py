import csv


class Save_csv:
    """Класс сохранения в csv файл"""

    def __init__(self):
        pass

    # Подготовка данных
    def write_csv(self, cnt_ready, count_recipes, time):
        self.cnt_ready = cnt_ready
        self.count_recipes = count_recipes
        hour = time.total_seconds() // 3600
        minutes = (time.total_seconds() // 60) % 60
        sec = time.total_seconds()
        self.time = f"{hour}:{minutes}:{sec}"
        with open("count.csv", "r", encoding="utf8") as f:
            read = csv.reader(f, delimiter=",")
            head = next(read, False)
            if head:
                for row in read:
                    old_hour, old_minuets, old_sec = row[2].split(":")
                    old_hour, old_minuets, old_sec = (
                        int(old_hour),
                        int(old_minuets),
                        float(old_sec),
                    )
                    hour += old_hour
                    minutes += old_minuets
                    sec += old_sec
                    if sec > 60:
                        minutes += (sec) // 60
                        sec = (sec) % 60
                    if minutes > 60:
                        hour += (minutes) // 60
                        minutes = (minutes) % 60
                    self.time = f"{int(float(hour))}:{int(float(minutes))}:{sec}"
        self.save()

    # Загруска файла csv в программу
    def load_open(self):
        with open("count.csv", "r", encoding="utf8") as f:
            read = csv.reader(f, delimiter=",")
            next(f)
            for row in read:
                hour, minutes, sec = row[2].split(":")
                total_hour = int(hour)
                return row[0], total_hour

    # Сохранение в csv
    def save(self):
        with open("count.csv", "w", encoding="utf8") as f:
            f.write("count_ready,count_recipes,max_time\n")
            f.write(f"{self.cnt_ready}, {self.count_recipes}, {self.time}")
