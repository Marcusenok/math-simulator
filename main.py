import sys

import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from random import randrange

# создаем глобальные переменные для дальнейшего удобства
ID_POLSOVATELA = 0
SPISOK_S_RESYLTATAMI = []
SPISOK_S_OTVETAMI_POLSOVATELA = []
UROVEN_SLOGNOSTI = 0


# Создаем класс для окна входа или регистрации
class MyWidget(QMainWindow):
    # вносим небольшие изменения в форму и подгружаем дизайн
    def __init__(self):
        super().__init__()
        uic.loadUi('vhod.ui', self)
        self.setWindowTitle('Вход')
        self.setFixedSize(555, 515)
        self.vhhod.clicked.connect(self.vhod_v_ychetky)
        self.registrasia.clicked.connect(self.registrasia_uchetnou_zapisu)

    # функция предназначена для проверки правильности введённых пользователем данных для входа
    def vhod_v_ychetky(self):
        # проверка на пустоту строк
        global ID_POLSOVATELA
        if len(self.name.text()) == 0 or len(self.password.text()) == 0:
            self.predypregdenie.setText('Заполните все поля')
        else:
            try:
                # проверка на наличие пользователя в БД
                con = sqlite3.connect('Matf_trenager.db')
                cur = con.cursor()
                result = cur.execute("""SELECT id, name, password
                            FROM polsovateli
                            WHERE name LIKE ? AND password LIKE ?""", (self.name.text(), self.password.text())).fetchall()
                # если пользователь не обнаружен вход в учетную запись не произойдет
                if len(result) == 0:
                    self.predypregdenie.setText('Неправильный логин или пароль')
                # если все данные введены правильно то происходит вход в учетную запись
                else:
                    # определяем id пользователя для индивудуальной робаты с его данными
                    ID_POLSOVATELA = result[0][0]
                    # открываем стартовую страницу
                    self.start = Startova_stranica(self)
                    self.start.show()
                    self.close()
                con.close()
            except:
                self.predypregdenie.setText('Неправильный логин или пароль')

    # функция для открытия формы регистрации польбавателя
    def registrasia_uchetnou_zapisu(self):
        self.form_registrasia = Form_registrasii(self)
        self.form_registrasia.show()
        self.close()


# описываем класс для регистрации пользователя
class Form_registrasii(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    # вносим небольшие изменения в форму и подгружаем дизайн
    def initUI(self, args):
        uic.loadUi('reg.ui', self)
        self.setFixedSize(641, 532)
        self.setWindowTitle('Регистрация нового пользователя')
        self.registrasia.clicked.connect(self.registrasia_uchetnou_zapisu_atap_2)

    # функция для проверки уникальности данных нового пользователя
    # и также добавление нового пользователя в БД
    def registrasia_uchetnou_zapisu_atap_2(self):
        if self.name.text() == '' or self.password.text() == '':
            self.nadpis.setText('Заполните все поля')
        else:
            # проверка на длинну пароля и логина
            if len(self.name.text()) > 16 or len(self.password.text()) < 8:
                self.nadpis.setText('Слишком динный логин или слишком короткий пароль')
            else:
                proverka_na_unicalnost = True
                # запрос в БД для получения имён всех пользователей
                con = sqlite3.connect('Matf_trenager.db')
                cur = con.cursor()
                result = cur.execute("""SELECT name
                                            FROM polsovateli""").fetchall()
                # проверка уникальности имени нового пользователя
                for i in result:
                    name = i[0]
                    if name == self.name.text():
                        self.nadpis.setText('Такой логин уже существует')
                        proverka_na_unicalnost = False
                        break
                con.close()
                # если все данные введены верно то в Бд создается новая запись для пользователя
                if proverka_na_unicalnost:
                    # запрос для получения всех id пользователей
                    con = sqlite3.connect('Matf_trenager.db')
                    cur = con.cursor()
                    result = cur.execute("""SELECT id
                                            FROM polsovateli""").fetchall()
                    # нахождение максимального id и создание id для нового пользователя
                    maxi = (max(result)[0]) + 1
                    con.close()

                    # вносим в БД нового пользователя
                    con = sqlite3.connect('Matf_trenager.db')
                    cur = con.cursor()
                    cur.execute(f"""INSERT INTO polsovateli(name, password, id, reheno, reheno_pravilno, 
                                    reting, ocenka_prilogenia) 
                                    VALUES(?, ?, ?, ?, ?, ?, ?)""",
                                (self.name.text(),
                                 self.password.text(),
                                 maxi,
                                 0, 0, 0, 0))
                    # обьявляем новый id для нового пользователя для данной сесии
                    con.commit()
                    con.close()
                    global ID_POLSOVATELA
                    ID_POLSOVATELA = maxi
                    # открываем стартовую страницу
                    self.start = Startova_stranica(self)
                    self.start.show()
                    self.close()


# описывание класса для стартовой страницы
class Startova_stranica(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    # вносим небольшие изменения в форму и подгружаем дизайн
    def initUI(self, args):
        uic.loadUi('start.ui', self)
        self.setFixedSize(1045, 356)
        self.setWindowTitle('Математический тренажер')
        self.pushButton.clicked.connect(self.vihod_is_uchetki)
        self.profil.clicked.connect(self.prosmotr_profila)
        self.prostoi_uroven.clicked.connect(self.primeri_prostogo_urovna)
        self.sredni_urven.clicked.connect(self.primeri_srednego_urovna)
        self.slogni_uroven.clicked.connect(self.primeri_slognogo_urovna)
        self.pushButton_2.clicked.connect(self.ocenit_prilogenie)

        # ниже описан алгоритмс выведения рейтинга пользователей
        spisok_retinga = []
        spisok_polsovatele = []
        con = sqlite3.connect('Matf_trenager.db')
        cur = con.cursor()
        result = cur.execute(f"""SELECT reting, name FROM polsovateli""").fetchall()
        for i in result:
            spisok_retinga.append(int(i[0]))
        for i in result:
            spisok_polsovatele.append(i[1])
        maxi = 0
        for i in spisok_retinga:
            if i > maxi:
                maxi = i
        self.pervoe_mesto.setText('1 место  ' + str(spisok_polsovatele[int(spisok_retinga.index(maxi))]) +
                                  ' (рейтинг ' + str(maxi) + ')')
        spisok_retinga[spisok_retinga.index(maxi)] = 0
        maxi = 0
        for i in spisok_retinga:
            if i > maxi:
                maxi = i
        self.vtoroe_mesto.setText('2 место  ' + str(spisok_polsovatele[int(spisok_retinga.index(maxi))]) +
                                  ' (рейтинг ' + str(maxi) + ')')
        spisok_retinga[spisok_retinga.index(maxi)] = 0
        maxi = 0
        for i in spisok_retinga:
            if i > maxi:
                maxi = i
        self.tretie_mesto.setText('3 место  ' + str(spisok_polsovatele[int(spisok_retinga.index(maxi))]) +
                                  ' (рейтинг ' + str(maxi) + ')')
        con.close()

        global ID_POLSOVATELA

        # создаем запрос к БД для получения информации которую мы будем отображать на стартовой странице
        con = sqlite3.connect('Matf_trenager.db')
        cur = con.cursor()
        result = cur.execute(f"""SELECT name
                    FROM polsovateli
                    WHERE id = {ID_POLSOVATELA}""").fetchall()
        # с помощью полученной из БД информации изменяем пустую надпись
        self.name_polsovatela.setText(str(result[0][0]))
        con.close()

    # функция для выхода из учётной записи
    # также она перенапрявлят пользователя на окно входа
    def vihod_is_uchetki(self):
        self.form_vhod = MyWidget()
        self.form_vhod.show()
        self.close()

    # функция для открытия окна профиля
    def prosmotr_profila(self):
        self.form_profila = Stranica_profila(self)
        self.form_profila.show()
        self.close()

    # функция для открытия окна с протыми примерами
    def primeri_prostogo_urovna(self):
        self.prostoi_uroven = Prostoi_uroven(self)
        self.prostoi_uroven.show()
        self.close()

    # открываем форму с примерами средней сложности
    def primeri_srednego_urovna(self):
        self.slogni_uroven = Sredni_uroven(self)
        self.slogni_uroven.show()
        self.close()

    # открываем форму с примерами высокой сложности
    def primeri_slognogo_urovna(self):
        self.sredni_uroven = Slogni_uroven(self)
        self.sredni_uroven.show()
        self.close()

    # открываем форму для оценки приложения
    def ocenit_prilogenie(self):
        self.ocenka_prilogenia = Ocenit_prilogenie(self)
        self.ocenka_prilogenia.show()
        self.close()


# описываем класс для формы профиля
class Stranica_profila(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    # вносим небольшие изменения в форму и подгружаем дизайн
    def initUI(self, args):
        uic.loadUi('profil.ui', self)
        self.setFixedSize(366, 473)
        self.setWindowTitle('Профиль')
        self.vernytca.clicked.connect(self.vozvracenie_na_startovu_stranisy)

        global ID_POLSOVATELA

        # создаем запрос к БД для получения информации которую мы будем отображать на странице профиля
        con = sqlite3.connect('Matf_trenager.db')
        cur = con.cursor()
        result = cur.execute(f"""SELECT name, reheno, reheno_pravilno, reting 
                    FROM polsovateli
                    WHERE id = {ID_POLSOVATELA}""").fetchall()
        # с помощью полученной из БД информации изменяем пустые надписи
        self.name.setText(str(result[0][0]))
        self.vsego_recheno.setText(str(result[0][1]))
        self.pravilnie.setText(str(result[0][2]))
        self.reting.setText(str(result[0][3]))
        con.close()

    # функция для открытия окна профиля
    def vozvracenie_na_startovu_stranisy(self):
        self.start = Startova_stranica(self)
        self.start.show()
        self.close()


# описываем класс для формы с простыми примерами
class Prostoi_uroven(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    # вносим небольшие изменения в форму и подгружаем дизайн
    def initUI(self, args):
        uic.loadUi('forma_dla_rehenia_primerov.ui', self)
        self.setFixedSize(630, 511)
        self.setWindowTitle('Простой уровень')
        self.pushButton.clicked.connect(self.podgotovka_k_proverke)
        # отображаем в все line edit разные примеры простого уровня
        self.primer_1.setText(str(randrange(99)) + ' + ' + str(randrange(99)))
        self.primer_2.setText(str(randrange(10)) + ' + ' + str(randrange(99)))
        self.primer_3.setText(str(randrange(99)) + ' - ' + str(randrange(10)))
        self.primer_4.setText(str(randrange(99)) + ' - ' + str(randrange(99)))
        self.primer_5.setText(str(randrange(99)) + ' + ' + str(randrange(99)))
        self.primer_6.setText(str(randrange(12)) + ' - ' + str(randrange(50)))
        self.primer_7.setText(str(randrange(99)) + ' + ' + str(randrange(99)))
        self.primer_8.setText(str(randrange(10)) + ' - ' + str(randrange(99)))

        # в глобальную переменную вносим ответы на все примеры
        global SPISOK_S_RESYLTATAMI
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_1.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_2.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_3.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_4.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_5.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_6.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_7.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_8.text()))

    # в этой функции мы получаем ответы пользователя и перенаправляем его на форму проверки и результатов
    def podgotovka_k_proverke(self):
        global SPISOK_S_OTVETAMI_POLSOVATELA
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_1.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_2.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_3.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_4.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_5.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_6.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_7.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_8.text())

        global UROVEN_SLOGNOSTI
        UROVEN_SLOGNOSTI = 1

        self.itogi = Itogi(self)
        self.itogi.show()
        self.close()


# описываем класс для формы с примерами средней сложности(он практически ни чем не отличается от класса
# для простых примеров)
class Sredni_uroven(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)
        self.pushButton.clicked.connect(self.podgotovka_k_proverke)

    # вносим небольшие изменения в форму и подгружаем дизайн
    def initUI(self, args):
        uic.loadUi('forma_dla_rehenia_primerov.ui', self)
        self.setFixedSize(630, 511)
        self.setWindowTitle('Средний уровень')
        self.label.setText('Средний уровень: вычитание и сложение')
        self.label_10.setText('чисел до 10000, а также')
        self.label_2.setText('умножение однорзрядных чисел')
        # отображаем в все line edit разные примеры простого уровня
        self.primer_1.setText(str(randrange(1000)) + ' + ' + str(randrange(1000)))
        self.primer_2.setText(str(randrange(500)) + ' + ' + str(randrange(100)))
        self.primer_3.setText(str(randrange(10000)) + ' - ' + str(randrange(10000)))
        self.primer_4.setText(str(randrange(500)) + ' - ' + str(randrange(500)))
        self.primer_5.setText(str(randrange(10)) + ' * ' + str(randrange(10)))
        self.primer_6.setText(str(randrange(10)) + ' * ' + str(randrange(10)))
        self.primer_7.setText(str(randrange(10)) + ' * ' + str(randrange(10)))
        self.primer_8.setText(str(randrange(10)) + ' * ' + str(randrange(10)))

        # в глобальную переменную вносим ответы на все примеры
        global SPISOK_S_RESYLTATAMI
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_1.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_2.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_3.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_4.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_5.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_6.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_7.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_8.text()))

    # в этой функции мы получаем ответы пользователя и перенаправляем его на форму проверки и результатов
    def podgotovka_k_proverke(self):
        global SPISOK_S_OTVETAMI_POLSOVATELA
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_1.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_2.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_3.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_4.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_5.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_6.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_7.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_8.text())

        global UROVEN_SLOGNOSTI
        UROVEN_SLOGNOSTI = 2

        self.itogi = Itogi(self)
        self.itogi.show()
        self.close()


# описываем класс для формы с примерами самой высокой сложности(он практически ни чем не отличается от класса
# для простых примеров и от класса для средних примеров)
class Slogni_uroven(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)
        self.pushButton.clicked.connect(self.podgotovka_k_proverke)

    # вносим небольшие изменения в форму и подгружаем дизайн
    def initUI(self, args):
        uic.loadUi('forma_dla_rehenia_primerov.ui', self)
        self.setFixedSize(630, 511)
        self.setWindowTitle('Средний уровень')
        self.label.setText('Сложный уровень: вычитание и сложение')
        self.label_10.setText('чисел до 100000, а также')
        self.label_2.setText('умножение чисел с тремя разрядами и меньше')
        # отображаем в все line edit разные примеры простого уровня
        self.primer_1.setText(str(randrange(10000)) + ' + ' + str(randrange(10000)))
        self.primer_2.setText(str(randrange(5000)) + ' + ' + str(randrange(1000)))
        self.primer_3.setText(str(randrange(100000)) + ' - ' + str(randrange(100000)))
        self.primer_4.setText(str(randrange(5000)) + ' - ' + str(randrange(50000)))
        self.primer_5.setText(str(randrange(100)) + ' * ' + str(randrange(100)))
        self.primer_6.setText(str(randrange(100)) + ' * ' + str(randrange(100)))
        self.primer_7.setText(str(randrange(100)) + ' * ' + str(randrange(1000)))
        self.primer_8.setText(str(randrange(1000)) + ' * ' + str(randrange(1000)))

        # в глобальную переменную вносим ответы на все примеры
        global SPISOK_S_RESYLTATAMI
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_1.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_2.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_3.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_4.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_5.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_6.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_7.text()))
        SPISOK_S_RESYLTATAMI.append(eval(self.primer_8.text()))

    # в этой функции мы получаем ответы пользователя и перенаправляем его на форму проверки и результатов
    def podgotovka_k_proverke(self):
        global SPISOK_S_OTVETAMI_POLSOVATELA
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_1.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_2.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_3.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_4.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_5.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_6.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_7.text())
        SPISOK_S_OTVETAMI_POLSOVATELA.append(self.otvet_8.text())

        global UROVEN_SLOGNOSTI
        UROVEN_SLOGNOSTI = 3

        self.itogi = Itogi(self)
        self.itogi.show()
        self.close()


# описываем класс для формы итогов
class Itogi(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    # вносим небольшие изменения в форму и подгружаем дизайн
    def initUI(self, args):
        uic.loadUi('itogi.ui', self)
        self.setFixedSize(473, 515)
        self.setWindowTitle('Проверка результатов')
        global SPISOK_S_RESYLTATAMI, SPISOK_S_OTVETAMI_POLSOVATELA

        # отображаем резульаты пользователя
        self.otveti_polsovatela_1.setText('1)  ' + str(SPISOK_S_OTVETAMI_POLSOVATELA[0]))
        self.otveti_polsovatela_2.setText('2)  ' + str(SPISOK_S_OTVETAMI_POLSOVATELA[1]))
        self.otveti_polsovatela_3.setText('3)  ' + str(SPISOK_S_OTVETAMI_POLSOVATELA[2]))
        self.otveti_polsovatela_4.setText('4)  ' + str(SPISOK_S_OTVETAMI_POLSOVATELA[3]))
        self.otveti_polsovatela_5.setText('5)  ' + str(SPISOK_S_OTVETAMI_POLSOVATELA[4]))
        self.otveti_polsovatela_6.setText('6)  ' + str(SPISOK_S_OTVETAMI_POLSOVATELA[5]))
        self.otveti_polsovatela_7.setText('7)  ' + str(SPISOK_S_OTVETAMI_POLSOVATELA[6]))
        self.otveti_polsovatela_8.setText('8)  ' + str(SPISOK_S_OTVETAMI_POLSOVATELA[7]))

        # отображаем правильные резульаты
        self.pravilnie_otveti_1.setText('1)  ' + str(SPISOK_S_RESYLTATAMI[0]))
        self.pravilnie_otveti_2.setText('2)  ' + str(SPISOK_S_RESYLTATAMI[1]))
        self.pravilnie_otveti_3.setText('3)  ' + str(SPISOK_S_RESYLTATAMI[2]))
        self.pravilnie_otveti_4.setText('4)  ' + str(SPISOK_S_RESYLTATAMI[3]))
        self.pravilnie_otveti_5.setText('5)  ' + str(SPISOK_S_RESYLTATAMI[4]))
        self.pravilnie_otveti_6.setText('6)  ' + str(SPISOK_S_RESYLTATAMI[5]))
        self.pravilnie_otveti_7.setText('7)  ' + str(SPISOK_S_RESYLTATAMI[6]))
        self.pravilnie_otveti_8.setText('8)  ' + str(SPISOK_S_RESYLTATAMI[7]))

        # сравваем ответы пользователя и правильные ответы и находим колличество правильных оветов пользователя
        self.pravilnix_otvetov = 0
        for i in range(0, 8):
            if SPISOK_S_OTVETAMI_POLSOVATELA[i] == str(SPISOK_S_RESYLTATAMI[i]):
                self.pravilnix_otvetov += 1

        self.itogi.setText('Правильно решено: ' + str(self.pravilnix_otvetov) + ' из 8')
        self.na_startovy.clicked.connect(self.vozvracenie_na_startovu_stranisy)

        # получаем данные которые мы будем менять
        con = sqlite3.connect('Matf_trenager.db')
        cur = con.cursor()
        result = cur.execute(f"""SELECT reheno, reheno_pravilno, reting FROM polsovateli 
                                 WHERE id = {ID_POLSOVATELA}""").fetchall()
        self.reheno, self.reheno_pravilno = int(result[0][0]) + 8, int(result[0][1]) + self.pravilnix_otvetov
        self.reting = 0
        # узнаём сколько рейтинга получил пользователь за решённые задания
        global UROVEN_SLOGNOSTI
        if UROVEN_SLOGNOSTI == 1:
            self.reting = self.pravilnix_otvetov * 1
        elif UROVEN_SLOGNOSTI == 2:
            self.reting = self.pravilnix_otvetov * 2
        elif UROVEN_SLOGNOSTI == 3:
            self.reting = self.pravilnix_otvetov * 3
        self.reting += int(result[0][2])
        con.close()

        # меняем информацию в БД на более актуальную
        con = sqlite3.connect('Matf_trenager.db')
        cur = con.cursor()
        cur.execute(f"""UPDATE polsovateli
                        SET reheno = {self.reheno}, reheno_pravilno = {self.reheno_pravilno}, reting = {self.reting}
                        WHERE id = {ID_POLSOVATELA}""")
        con.commit()
        con.close()

        # не забываем очистить переменные
        SPISOK_S_RESYLTATAMI.clear()
        SPISOK_S_OTVETAMI_POLSOVATELA.clear()

    # открываем стартовую страницу
    def vozvracenie_na_startovu_stranisy(self):
        self.start = Startova_stranica(self)
        self.start.show()
        self.close()


# описываем класс для оценки приложения
class Ocenit_prilogenie(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    # вносим небольшие изменения в форму и подгружаем дизайн
    def initUI(self, args):
        uic.loadUi('ocenka_prilogenia.ui', self)
        self.setFixedSize(501, 360)
        self.setWindowTitle('Оценить приложение')
        self.ocenit.clicked.connect(self.ocenit_prilogenie)
        self.pushButton.clicked.connect(self.startovaa_stranica)
        con = sqlite3.connect('Matf_trenager.db')
        cur = con.cursor()
        result = cur.execute(f"""SELECT ocenka_prilogenia, id FROM polsovateli""").fetchall()
        symma = 0
        polsovateli = 0
        for i in result:
            if i[0] != 0:
                symma += int(i[0])
                polsovateli += 1
        self.label_3.setText('Общая оценка приложения сейчас ' + str(symma / polsovateli)[:4])
        con.close()

    # функция для ынесения оценки пользователя в БД
    def ocenit_prilogenie(self):
        global ID_POLSOVATELA
        con = sqlite3.connect('Matf_trenager.db')
        cur = con.cursor()
        result = cur.execute(f"""SELECT ocenka_prilogenia FROM polsovateli 
                        WHERE id = {ID_POLSOVATELA}""").fetchall()
        if result[0][0] != 0:
            self.predypregdenie.setText('Вы уже выставили оценку ранее')
        else:
            if int(self.lineEdit.text()) > 10 or int(self.lineEdit.text()) < 1:
                self.predypregdenie.setText('Такой оценки не может быть')
            else:
                con = sqlite3.connect('Matf_trenager.db')
                cur = con.cursor()
                result = cur.execute(f"""UPDATE polsovateli 
                                        SET ocenka_prilogenia = {int(self.lineEdit.text())}
                                       WHERE id = {ID_POLSOVATELA}""").fetchall()
                self.predypregdenie.setText('Спасибо за вашу оценку!')
                con.commit()
                con.close()
        con.close()

    def startovaa_stranica(self):
        self.start = Startova_stranica(self)
        self.start.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())