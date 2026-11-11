import csv
import io
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget,
    QApplication,
    QMainWindow,
    QFileDialog,
    QVBoxLayout,
    QTextEdit,
    QLabel,
    QPushButton,
    QStackedWidget,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut
import datetime as dt
import sqlite3
import os

style = """
QMainWindow { background-color: #f0f0f0; color: #000000; }
QTextBrowser { background-color: #ffffff; color: #000000; border: 2px solid #cccccc; border-radius: 6px; padding: 7px; }
QLineEdit { background-color: #ffffff; color: #000000; border: 2px solid #cccccc; border-radius: 6px; padding: 2px 5px; }
QPushButton { background-color: #004494; color: #ffffff; border-radius: 6px; padding: 7px; }
QPushButton:hover {background-color: #4da3ff; }
QLineEdit:focus {border: 2px solid #004494; padding: 0px 3px; }
"""

signal_name = []


class Recipe(QWidget):
    """Второй класс окно. В нем можно записать новый рецепт"""

    def __init__(self):
        super().__init__()
        uic.loadUi("Шаблоны/recipe.ui", self)
        self.setStyleSheet(style)
        self.setWindowTitle("Рецепт")

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        while self.recipe.count() > 0:
            widget = self.recipe.widget(0)
            self.recipe.removeWidget(widget)

        self.flag_who = "new"

        self.left = QShortcut(QKeySequence("Left"), self)
        self.left.activated.connect(lambda sign="-": self.moving(sign))

        self.right = QShortcut(QKeySequence("Right"), self)
        self.right.activated.connect(lambda sign="+": self.moving(sign))

        self.save_Button.clicked.connect(self.save)
        self.add.clicked.connect(self.new_point)

    # Добавление в SteckWidget пункта
    def new(self):
        self.new_point()
        self.name.setText("Введите название рецепта")

    def old(self, input_name):
        self.input_name = input_name
        self.flag_who = "old"
        con = sqlite3.connect("Базы данных/points.db")
        cur = con.cursor()
        result = cur.execute(
            """SELECT name, point FROM recipe WHERE name = ?""", (input_name,)
        ).fetchall()
        self.name.setText(result[0][0])
        list_point = result[0][1].split(",00 35 ")
        for i in range(len(list_point)):
            new_widget = QWidget()
            layout = QVBoxLayout(new_widget)

            txt = QTextEdit()
            txt.setPlainText(list_point[i])
            layout.addWidget(txt)

            self.recipe.addWidget(new_widget)

    # Новый пункт
    def new_point(self):
        new_widget = QWidget()
        layout = QVBoxLayout(new_widget)

        txt = QTextEdit()
        layout.addWidget(txt)

        self.recipe.addWidget(new_widget)
        self.recipe.setCurrentWidget(new_widget)

    # Перемещение по SteckWidget
    def moving(self, sign):
        tot_widget = self.recipe.count()
        current_indx = self.recipe.currentIndex()
        if sign == "-":
            current_indx = current_indx - 1
        else:
            current_indx = current_indx + 1

        if 0 <= current_indx <= tot_widget:
            self.recipe.setCurrentIndex(current_indx)

    # Перемещение курсора
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        focused_widget = self.focusWidget()
        if focused_widget:
            focused_widget.clearFocus()

    # Сохранение
    def save(self):
        name_recipe = self.name.toPlainText().rstrip().lstrip()
        if len(name_recipe) <= 2:
            self.name.setPlainText("Должно быть больше 2 символов!!!")
        else:
            list_recipe = []
            for i in range(self.recipe.count()):
                textedit = self.recipe.widget(i).findChild(QTextEdit)
                txt = textedit.toPlainText().rstrip().lstrip()
                list_recipe.append(txt)
            str_recipe = ",00 35 ".join(list_recipe)
            signal_name.append(name_recipe)
            con = sqlite3.connect("Базы данных/arts.db")
            cur = con.cursor()
            cur.execute(
                """INSERT OR IGNORE INTO art(name) VALUES(?) ON CONFLICT (name) DO NOTHING""",
                (name_recipe,),
            )
            con.commit()
            con.close()
            con = sqlite3.connect("Базы данных/points.db")
            cur = con.cursor()
            if self.flag_who == "new":
                cur.execute(
                    """INSERT OR IGNORE INTO recipe(name, point) VALUES(?, ?) ON CONFLICT (name) DO NOTHING""",
                    (
                        name_recipe,
                        str_recipe,
                    ),
                )
                con.commit()

                if cur.rowcount == 0:
                    self.name.setPlainText(
                        f"{self.name.toPlainText()}\nЗапись с таким именем уже есть"
                    )
                    return
            else:
                cur.execute(
                    """UPDATE recipe 
                    SET name = ?, point = ?
                    WHERE name = ?""",
                    (
                        name_recipe,
                        str_recipe,
                        self.input_name,
                    ),
                )
                con.commit()
            con.close()
            self.close()


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


class Main(QMainWindow):
    """Главны класс. В нем можно довбавлять, изменять, открывать, удалять рецепты."""

    def __init__(self):
        super().__init__()
        uic.loadUi("Шаблоны/main_window.ui", self)
        self.setStyleSheet(style)
        self.list_window = []
        self.setWindowTitle("Книга рецептов")
        pixmap = QPixmap("картинка на добавить.jpg")
        scaled_pixmap = pixmap.scaled(
            700,
            400,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.art.setPixmap(scaled_pixmap)
        self.time.setDigitCount(5)
        value_ready, self.total_hour = Save_csv().load_open()
        value_ready = int(value_ready)
        self.count_ready.setValue(value_ready)
        self.start_time = dt.datetime.now()
        self.arts = QStackedWidget()
        self.elements.insertWidget(0, self.arts)

        cnt = 0
        if not os.path.isfile("Базы данных/points.db"):
            cnt += 1
            con = sqlite3.connect("Базы данных/points.db")
            cur = con.cursor()

            cur.execute("""CREATE TABLE recipe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                point TEXT)""")
            con.commit()
            con.close()

        if not os.path.isfile("Базы данных/arts.db"):
            cnt += 1
            con = sqlite3.connect("Базы данных/arts.db")
            cur = con.cursor()

            cur.execute("""CREATE TABLE art (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                name_art TEXT)""")
            con.commit()
            con.close()

        if cnt == 2:
            con = sqlite3.connect("Базы данных/arts.db")
            cur = con.cursor()

            cur.execute("""INSERT INTO art(name) VALUES('Пирог')""")
            con.commit()
            con.close()

            con = sqlite3.connect("Базы данных/points.db")
            cur = con.cursor()

            cur.execute("""INSERT INTO recipe(name, point) VALUES('Пирог', '1,00 35 2')""")
            con.commit()
            con.close()

        self.repair()
        self.addButton.clicked.connect(self.new_recipe)
        self.open_Button.clicked.connect(self.open_change)
        self.del_Button.clicked.connect(self.dele)

        self.addart_Button.clicked.connect(self.add_art)

        self.recipes_list.currentRowChanged.connect(self.switch_page)

        self.start_Button.clicked.connect(self.start)
        self.stop_Button.setEnabled(False)
        self.stop_Button.clicked.connect(self.stop)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

    def repair(self):
        con = sqlite3.connect("Базы данных/points.db")
        cur = con.cursor()

        result = cur.execute("""SELECT name FROM recipe""")
        for i in result:
            i = i[0]
            new_widget = QWidget()
            layout = QVBoxLayout(new_widget)
            art = QLabel()
            layout.addWidget(art)
            self.arts.addWidget(new_widget)
            self.recipes_list.addItem(i)
            self.statusBar().showMessage(
                f"Кол-во {len(self.recipes_list)} рецептов, кол-во часов {self.total_hour}"
            )
        con.close()

        con = sqlite3.connect("Базы данных/arts.db")
        cur = con.cursor()

        result = cur.execute("""SELECT name_art FROM art""").fetchall()

        for i in range(len(result)):
            way = result[i][0]
            current_widget = self.arts.widget(i)
            label_widget = current_widget.findChild(QLabel)
            pixmap = QPixmap(way)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    350,
                    350,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                label_widget.setPixmap(scaled_pixmap)
        con.close()

    # Создание второго окна
    def new_recipe(self):
        window_recipe = Recipe()
        window_recipe.new()
        self.list_window.append(window_recipe)
        window_recipe.destroyed.connect(lambda: self.remove(window_recipe))
        window_recipe.destroyed.connect(self.add_recipe)
        window_recipe.show()

    # Удаление окна из списка окон
    def remove(self, window_recipe):
        if window_recipe in self.list_window:
            self.list_window.remove(window_recipe)

    # Добавление картинки
    def add_art(self):
        if self.recipes_list.currentRow() != -1:
            fname = QFileDialog.getOpenFileName(
                self,
                "Выбрать картинку",
                "",
                "Картинка (*.jpg);;Картинка (*.png);;Картинка (*.webp);",
            )[0]
            if fname:
                current_widget = self.arts.currentWidget()
                label_widget = current_widget.findChild(QLabel)
                pixmap = QPixmap(fname)
                scaled_pixmap = pixmap.scaled(
                    350,
                    350,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                label_widget.setPixmap(scaled_pixmap)
            con = sqlite3.connect("Базы данных/arts.db")
            cur = con.cursor()

            result = cur.execute(
                """UPDATE art
                    SET name_art = ?
                    WHERE name = ?""",
                (
                    fname,
                    self.recipes_list.item(self.index).text(),
                ),
            )
            con.commit()
            con.close()
        else:
            self.statusBar().showMessage("Не выбран рецепт или нет рецептов")

    # Запись названия в recipes_list
    def add_recipe(self):
        if signal_name != []:
            new_name = signal_name[0]
            if new_name not in [
                self.recipes_list.item(i).text()
                for i in range(self.recipes_list.count())
            ]:
                new_widget = QWidget()
                layout = QVBoxLayout(new_widget)
                art = QLabel()
                layout.addWidget(art)
                self.arts.addWidget(new_widget)
                self.recipes_list.addItem(new_name)
                self.statusBar().showMessage(
                    f"Кол-во {len(self.recipes_list)} рецептов, кол-во часов {self.total_hour}"
                )
        signal_name.clear()

    # Перемещение по recipes_list
    def switch_page(self, index):
        self.index = self.recipes_list.currentRow()
        self.arts.setCurrentIndex(index)
        count_recipes = len(self.recipes_list)
        if count_recipes % 100 == 0:
            self.statusBar().showMessage(
                f"Поздравляем у тебя целых {count_recipes} рецептов"
            )
        else:
            self.statusBar().showMessage(
                    f"Кол-во {len(self.recipes_list)} рецептов, кол-во часов {self.total_hour}"
                )

    # Метод для старта таймера
    def start(self):
        input_time = self.cnt_time.time()
        self.dt_time = input_time
        input_time = input_time.toString("hh:mm")
        self.timer.start(60000)
        self.start_Button.setEnabled(False)
        self.stop_Button.setEnabled(True)
        self.time.display(input_time)

    # Метод обновление таймера
    def update_timer(self):
        self.dt_time = self.dt_time.addSecs(-60)
        str_time = self.dt_time.toString("hh:mm")
        self.time.display(str_time)
        if str_time == "00:00":
            self.stop()

    # Метод остоновки таймера
    def stop(self):
        self.stop_Button.setEnabled(False)
        self.start_Button.setEnabled(True)
        self.time.display("00:00")
        self.timer.stop()

    # Метод кнопки открытия второго окна
    def open_change(self):
        window_recipe = Recipe()
        name = self.recipes_list.item(self.index).text()
        window_recipe.old(name)
        self.list_window.append(window_recipe)
        window_recipe.destroyed.connect(lambda: self.remove(window_recipe))
        window_recipe.destroyed.connect(self.update_recipe)
        window_recipe.show()

    def update_recipe(self):
        if signal_name != []:
            new_name = signal_name[0]
            if new_name not in [
                self.recipes_list.item(i).text()
                for i in range(self.recipes_list.count())
            ]:
                self.recipes_list.item(self.index).setText(new_name)
        signal_name.clear()

    # Удаляет рецепт из recipes_list
    def dele(self):
        con = sqlite3.connect("Базы данных/arts.db")
        cur = con.cursor()

        cur.execute(
            """DELETE FROM art WHERE name = ?""",
            (self.recipes_list.item(self.index).text(),),
        )

        con.commit()
        con.close()

        con = sqlite3.connect("Базы данных/points.db")
        cur = con.cursor()

        cur.execute(
            """DELETE FROM recipe WHERE name = ?""",
            (self.recipes_list.item(self.index).text(),),
        )

        con.commit()
        con.close()
        
        recipe = self.recipes_list.takeItem(self.index)
        del recipe

    # Диалоговое окно закрытия
    def closeEvent(self, event):
        wind_question = QMessageBox.question(
            self,
            "Закрытие программы",
            "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if wind_question == QMessageBox.StandardButton.Yes:
            end_time = dt.datetime.now()
            difference = end_time - self.start_time
            save = Save_csv()
            save.write_csv(self.count_ready.value(), len(self.recipes_list), difference)
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec())
