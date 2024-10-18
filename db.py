import mysql.connector
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Função para conectar ao banco de dados
def get_db_connection():
    try:
        # Primeiro, conecta-se ao MySQL sem especificar o banco de dados
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', 3306)  # Porta padrão é 3306 se não especificada
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            # Criar o banco de dados se ele não existir
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')};")
            print(f"Banco de dados '{os.getenv('DB_NAME')}' criado com sucesso ou já existe.")
            connection.database = os.getenv('DB_NAME')  # Conecta ao banco de dados criado
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    hash TEXT NOT NULL,
                    movies TEXT
                );
            """)
            # Criar tabela favorites se não existir
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    title VARCHAR(100) NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)
            connection.commit()  # Confirma as criações das tabelas
            print(f"Tabelas 'users' e 'favorites' criadas com sucesso ou já existem.")

            cursor.close()  # Feche o cursor após criar o banco de dados

            # Conectar novamente, agora ao banco de dados
            return connection
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao MySQL: {err}")
        return None

# Função para fechar a conexão
def close_db_connection(connection):
    if connection.is_connected():
        connection.close()
        print("Conexão foi encerrada.")