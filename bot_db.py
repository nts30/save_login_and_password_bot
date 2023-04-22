import sqlite3 as sqlite
from sqlite3 import IntegrityError
from typing import Generator


class Database:
    def __init__(self, db_file: str) -> None:
        self.connection = sqlite.connect(db_file)
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self):
        if self.connection:
            print('Database connected')
        with self.connection:
            self.cursor.execute('CREATE TABLE IF NOT EXISTS accounts('
                                'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
                                'login TEXT UNIQUE,'
                                'password TEXT)')
            self.connection.commit()

    def add_account(self, login: str, password: str) -> str:
        try:
            with self.connection:
                self.cursor.execute('INSERT INTO accounts (login, password) VALUES (?, ?)', (login, password))
                self.connection.commit()
                return 'Добавлен новый пользователь!'
        except IntegrityError:
            return 'Данные не сохранены, такой логин уже существует'

    def read_info(self) -> Generator:
        with self.connection:
            all_info = self.cursor.execute('SELECT * FROM accounts').fetchall()
            if not all_info:
                yield 'Нет аккаунтов'
            for info in all_info:
                login = info[1]
                password = info[-1]
                yield f'Логин: {login} | Пароль: {password}'

    def _check_login(self, login: str) -> list:
        with self.connection:
            logins = self.cursor.execute('SELECT login FROM accounts WHERE login = ?', (login,)).fetchall()
            return logins

    def delete_account(self, login: str) -> str:
        with self.connection:
            if self._check_login(login):
                self.cursor.execute('DELETE FROM accounts WHERE login = ?', (login,))
                self.connection.commit()
                return 'Аккаунт успешно удален'
            else:
                return 'Аккаунт не найден'

    def delete_all_accounts(self):
        with self.connection:
            self.cursor.execute('DELETE FROM accounts')
        return 'Все аккаунты удалены'


if __name__ == '__main__':
    db = Database('users_bot')
    db.add_account('artem_2', '123456')
    print(db.read_info())
    print(db.delete_account('artem_2'))
