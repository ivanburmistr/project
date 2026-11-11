# НА РУССКОМ

# Книга рецептов
---
## Цель
---
Улучшить книгу рецептов, которая была на бумаге.
## Что использовал
---
- Pyqt6
как скачать
```
    python -m venv venv
    venv/Scripts/activate
    pip install pyqt6
```
## Возможности
---
- __Создание и редактировани:__
создание новых рецептов и изменение.
- __Визуализация__
загруска фото блюд
## Что есть
---
- _Таймер_
- _картинка_
- _Переключение стрелочками_
- _Подсчет количества готовых блюд_
## Работа с приложением
- В меню "Рецепты" кнопка открыть открывает окно, в котором есть то, что писал пользователь, и это можно изменять. Добавлять картинки на каждый рецепт.
- В меню "Добавить" кнопка добавить пересылает на второе окно, в котором можно записать пункты рецептов.
  - Во втором окне есть:
    - название (больше двух символов)
    - пункты
    - кнопка добавить (добавляет пункт)
    - примечание
- В меню "Таймер" есть таймер.
# ВАЖНО
- Если вы изменяете путь картинки или переименовываете папку или картинку, то при переносе картинки из папки или диска, вы должны изменить в базе данных "arts.db" путь в столбце name_art на новый или передобавить картинку в программе. Лучше если вы создадите папку в которой будут все картинки и из этой папки вы сможете добавлять картинки.

# НА АНГЛИЙСКОМ

# Recipe Book
---
## Goal
---
Improve the recipe book that was on paper.
Make the websites better. 
## What I used
---
- Pyqt6
how to download
```
 python -m venv venv
 venv/Scripts/activate
 pip install pyqt6
```
## Features
---
- __Creation and editing:__
creating new recipes and modifying existing ones.
- __Visualization__
loading photos of dishes
## What’s available
---
- _Timer_
- _Image_
- _Switching with arrows_
- _Counting the number of completed dishes_
## Working with the app
- In the “Recipes” menu, the “Open” button opens a window containing what the user wrote, and this can be modified.
- In the “Add” menu, the “Add” button redirects to a second window where you can write recipe items.
 - The second window contains:
 - a title (more than two characters)
 - items
 - an add button (adds an item)
 - a note
- The “Timer” menu contains a timer.

# IMPORTANT
- If you change the path to the image or rename the folder or image, then when moving the image from the folder or disk, you must change the path in the name_art column in the “arts.db” database to the new one, or re‑add the image in the program. It’s better if you create a folder that will contain all the images, and you can add images from that folder.