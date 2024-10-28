import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import cv2
import pymysql
import os
import hashlib

# Configurações do banco de dados
db_config = {
    'user': 'root',
    'password': '12345678',
    'host': 'localhost',
    'database': 'bancodeteste'
}

# Função para conectar ao banco de dados
def conectar_bd():
    return pymysql.connect(**db_config)

# Função para criptografar a senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Função para capturar e salvar a imagem facial
def capturar_imagem_facial(login):
    camera = cv2.VideoCapture(0)
    caminho_imagem = f"imagens/{login}.jpg"

    if not camera.isOpened():
        print("Falha ao acessar a câmera.")
        messagebox.showerror("Erro", "Não foi possível acessar a câmera.")
        return None

    cv2.namedWindow("Captura Facial")

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Falha ao capturar imagem.")
            break
        cv2.imshow("Captura Facial", frame)

        # Pressionar 'Espaço' para capturar
        if cv2.waitKey(1) % 256 == 32:
            cv2.imwrite(caminho_imagem, frame)
            print(f"Imagem capturada e salva em: {caminho_imagem}")
            break

    camera.release()
    cv2.destroyAllWindows()
    return caminho_imagem

# Função para registrar o usuário
def cadastrar_usuario(login, senha):
    caminho_imagem = f"imagens/{login}.jpg"
    
    conexao = conectar_bd()
    cursor = conexao.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO usuarios (login, senha, caminho_imagem) VALUES (%s, %s, %s)",
            (login, hash_senha(senha), caminho_imagem)
        )
        conexao.commit()
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
    except pymysql.IntegrityError:
        messagebox.showerror("Erro", "O login já existe.")
    finally:
        cursor.close()
        conexao.close()

# Função para realizar login
def login_usuario(login, senha):
    conexao = conectar_bd()
    cursor = conexao.cursor()
    
    try:
        cursor.execute("SELECT senha, caminho_imagem FROM usuarios WHERE login = %s", (login,))
        resultado = cursor.fetchone()
        
        if resultado:
            senha_bd, caminho_imagem = resultado
            if hash_senha(senha) == senha_bd:
                # Capturar imagem facial
                if capturar_imagem_facial(login) is not None:
                    messagebox.showinfo("Sucesso", "Login bem-sucedido!")
            else:
                messagebox.showerror("Erro", "Senha incorreta!")
        else:
            messagebox.showerror("Erro", "Usuário não encontrado.")
    finally:
        cursor.close()
        conexao.close()

# Função para abrir a janela de cadastro
def abrir_cadastro():
    def cadastrar():
        login = entry_login.get()
        senha = entry_senha.get()
        if not login or not senha:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos.")
            return
        if capturar_imagem_facial(login) is not None:
            cadastrar_usuario(login, senha)

    janela_cadastro = tk.Toplevel()
    janela_cadastro.title("Cadastro")
    janela_cadastro.configure(bg="blue")  # Cor de fundo azul
    centralizar_janela(janela_cadastro, 300, 250)  # Centraliza a janela

    ttk.Label(janela_cadastro, text="Cadastro", font=("Helvetica", 14), background="blue", foreground="black").pack(pady=10)

    ttk.Label(janela_cadastro, text="Login:", background="blue", foreground="black").pack(pady=5)
    entry_login = ttk.Entry(janela_cadastro)
    entry_login.pack(pady=5)

    ttk.Label(janela_cadastro, text="Senha:", background="blue", foreground="black").pack(pady=5)
    entry_senha = ttk.Entry(janela_cadastro, show="*")
    entry_senha.pack(pady=5)

    ttk.Button(janela_cadastro, text="Cadastrar", command=cadastrar, style="Accent.TButton").pack(pady=10)

# Função para abrir a janela de login
def abrir_login():
    def login():
        login = entry_login.get()
        senha = entry_senha.get()
        if not login or not senha:
            messagebox.showwarning("Atenção", "Por favor, preencha todos os campos.")
            return
        login_usuario(login, senha)

    janela_login = tk.Toplevel()
    janela_login.title("Login")
    janela_login.configure(bg="blue")  # Cor de fundo azul
    centralizar_janela(janela_login, 300, 250)  # Centraliza a janela

    ttk.Label(janela_login, text="Login", font=("Helvetica", 14), background="blue", foreground="black").pack(pady=10)

    ttk.Label(janela_login, text="Login:", background="blue", foreground="black").pack(pady=5)
    entry_login = ttk.Entry(janela_login)
    entry_login.pack(pady=5)

    ttk.Label(janela_login, text="Senha:", background="blue", foreground="black").pack(pady=5)
    entry_senha = ttk.Entry(janela_login, show="*")
    entry_senha.pack(pady=5)

    ttk.Button(janela_login, text="Entrar", command=login, style="Accent.TButton").pack(pady=10)

# Função para centralizar a janela
def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")

# Função principal para a interface gráfica
def main():
    os.makedirs("imagens", exist_ok=True)
    
    root = tk.Tk()
    root.title("Sistema de Cadastro e Login")
    root.geometry("400x300")
    root.configure(bg="blue")  # Cor de fundo azul

    style = ttk.Style()
    style.configure("Accent.TButton", background="#4CAF50", foreground="black", font=("Helvetica", 12))
    style.map("Accent.TButton", background=[("active", "#45a049")])

    ttk.Label(root, text="Bem-vindo ao sistema de cadastro e login", font=("Helvetica", 12), background="blue", foreground="black").pack(pady=10)

    ttk.Button(root, text="Cadastrar", command=abrir_cadastro, width=20, style="Accent.TButton").pack(pady=5)
    ttk.Button(root, text="Login", command=abrir_login, width=20, style="Accent.TButton").pack(pady=5)

    centralizar_janela(root, 400, 300)  # Centraliza a janela principal

    root.mainloop()

if __name__ == "__main__":
    main()
