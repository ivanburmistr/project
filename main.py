import sys
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget,
    QApplication,
    QMainWindow,
    QFileDialog,
    QVBoxLayout,
    QLabel,
    QStackedWidget,
    QMessageBox,
    QSizePolicy,
)
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QPixmap
import datetime as dt
import sqlite3
import os
from PyQt6.QtMultimedia import QSoundEffect
from classes.recipe import Recipe
from classes.signal import signal_name
from classes.save_csv import Save_csv

style = """
QMainWindow { background-color: #f0f0f0; color: #000000; }
QPushButton { background-color: #004494; color: #ffffff; border-radius: 6px; padding: 7px; }
QPushButton:hover {background-color: #4da3ff; }
"""


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

        self.add = QShortcut(QKeySequence("Ctrl+O"), self)
        self.add.activated.connect(self.new_recipe)
        self.change = QShortcut(QKeySequence("Ctrl+U"), self)
        self.change.activated.connect(self.open_change)
        self.delet_recipe = QShortcut(QKeySequence("Delete"), self)
        self.delet_recipe.activated.connect(self.dele)
        self.hot_art = QShortcut(QKeySequence("Ctrl+A"), self)
        self.hot_art.activated.connect(self.add_art)
        self.orig_art = {}
        self.art.setPixmap(scaled_pixmap)
        self.time.setDigitCount(8)
        self.time.display("00:00:00")
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

            cur.execute(
                """INSERT INTO recipe(name, point) VALUES('Пирог', '1,00 35 2')"""
            )
            con.commit()
            con.close()

        self.cnt = 0

        self.alaram_sound = QSoundEffect()
        self.alaram_sound.setSource(QUrl.fromLocalFile("таймер звук.wav"))
        self.alaram_sound.setVolume(0.8)
        self.alaram_sound.setLoopCount(QSoundEffect.Loop.Infinite.value)

        self.tabWidget.currentChanged.connect(self.update_image)
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

    # База данных
    def repair(self):
        con = sqlite3.connect("Базы данных/points.db")
        cur = con.cursor()

        result = cur.execute("""SELECT name FROM recipe""")
        for i in result:
            i = i[0]
            new_widget = QWidget()
            layout = QVBoxLayout(new_widget)
            art = QLabel()
            art.setMinimumSize(1, 1)
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
                self.update_image()
                self.orig_art[label_widget] = pixmap
        self.arts.widget(0)
        con.close()

    def update_image(self):
        try:
            if len(self.recipes_list) != 0:
                current_widget = self.arts.currentWidget()
                label_widget = current_widget.findChild(QLabel)
                label_widget.setSizePolicy(
                    QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
                )
                pixmap = self.orig_art.get(label_widget)
                if pixmap:
                    scaled_pixmap = pixmap.scaled(label_widget.size())
                    label_widget.setPixmap(scaled_pixmap)
            self.art.setSizePolicy(
                QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
            )
            pixmap = QPixmap("картинка на добавить.jpg")
            if pixmap:
                scaled_pixmap = pixmap.scaled(self.art.size())
                self.art.setPixmap(scaled_pixmap)
        except Exception:
            pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self.update_image)

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
                self.orig_art[label_widget] = pixmap
                self.update_image()
            con = sqlite3.connect("Базы данных/arts.db")
            cur = con.cursor()

            cur.execute(
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
                art.setMinimumSize(1, 1)
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
        self.update_image()

    # Метод для старта таймера
    def start(self):
        input_time = self.cnt_time.time()
        self.dt_time = input_time
        self.start_Button.setEnabled(False)
        self.stop_Button.setEnabled(True)
        input_time = input_time.toString("hh:mm:ss")
        if input_time == "00:00:00":
            self.stop()
            return
        self.timer.start(1000)

        self.time.display(input_time)

    # Метод обновление таймера
    def update_timer(self):
        self.dt_time = self.dt_time.addSecs(-1)
        str_time = self.dt_time.toString("hh:mm:ss")
        self.time.display(str_time)
        if str_time == "00:00:00":
            self.stop()

    # Метод остоновки таймера
    def stop(self):
        self.cnt += 1
        if self.cnt == 1:
            self.alaram_sound.play()
            self.timer.stop()
            self.time.display("00:00:00")
            self.tabWidget.setCurrentIndex(2)
        elif self.cnt == 2:
            self.stop_Button.setEnabled(False)
            self.start_Button.setEnabled(True)
            self.alaram_sound.stop()
            self.cnt = 0

    # Метод кнопки открытия второго окна
    def open_change(self):
        if self.recipes_list.currentRow() != -1:
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
        if self.recipes_list.currentRow() != -1:
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

            widget = self.arts.widget(self.index)
            if widget in self.orig_art:
                del self.orig_art[widget]
            self.arts.removeWidget(widget)
            widget.deleteLater()
            recipe = self.recipes_list.takeItem(self.index)
            del recipe
            self.statusBar().showMessage(
                f"Кол-во {len(self.recipes_list)} рецептов, кол-во часов {self.total_hour}"
            )

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
