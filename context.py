from telegram.ext import Application, CallbackContext

class pyodbcContext(CallbackContext):
    def __init__(self, application, chat_id, user_id, cursor):
        print("New pyodbc context")
        super().__init__(application, chat_id, user_id)
        self._cursor = cursor
        

    @property
    def cursor(self):
        if self._cursor:
            return self.cursor
        return
    @cursor.setter
    def cursor(self, cursor):
        self._cursor = cursor