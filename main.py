from database import init_db
from bot import start_polling

def main():
    init_db()  # Initialiser la base de données et créer les tables
    start_polling()  # Démarrer le bot


if __name__ == '__main__':
    main()