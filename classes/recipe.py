from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
)
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
import sqlite3
from classes.signal import signal_name

style = """
QMainWindow { background-color: #26721d; color: #000000; }
QPushButton { background-color: #26721d; color: #ffffff; border-radius: 6px; padding: 7px; }
QPushButton:hover {background-color: #28a919; }
"""


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
        self.delpoint_Button.clicked.connect(self.delet_point)

    # Удаление из SteckWidget
    def delet_point(self):
        widget = self.recipe.currentWidget()
        if widget is not None:
            self.recipe.removeWidget(widget)
            widget.deleteLater()

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

            if self.flag_who == "new":
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

                cur.execute(
                    """INSERT OR IGNORE INTO recipe(name, point) VALUES(?, ?) ON CONFLICT (name) DO NOTHING""",
                    (
                        name_recipe,
                        str_recipe,
                    ),
                )
                con.commit()
                con.close()

                if cur.rowcount == 0:
                    self.name.setPlainText(
                        f"{self.name.toPlainText()}\nЗапись с таким именем уже есть"
                    )
                    return
            else:
                con = sqlite3.connect("Базы данных/points.db")
                cur = con.cursor()

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

                con2 = sqlite3.connect("Базы данных/arts.db")
                cur2 = con2.cursor()

                cur2.execute(
                    """UPDATE art 
                    SET name = ?
                    WHERE name = ?""",
                    (
                        name_recipe,
                        self.input_name,
                    ),
                )
                con2.commit()
                con2.close()
            self.close()
