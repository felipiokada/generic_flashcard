import tkinter as tk
import json
import os
import random
from datetime import datetime, timedelta

ARQUIVO_BARALHOS = "baralhos.json"

def carregar_baralhos():
    if os.path.exists(ARQUIVO_BARALHOS):
        with open(ARQUIVO_BARALHOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_novo_baralho(nome_baralho):
    baralhos = carregar_baralhos()
    baralhos.append({"nome": nome_baralho, "data_criacao": datetime.now().strftime("%Y-%m-%d"), "data_ultimo_estudo": None, "vezes_estudado": 0,"cartoes":[]})
    with open(ARQUIVO_BARALHOS, "w", encoding="utf-8") as f:
        json.dump(baralhos, f, indent=4, ensure_ascii=False)

def salvar_renomear_baralho(nome_antigo, nome_novo):
    baralhos = carregar_baralhos()
    for baralho in baralhos:
        if baralho["nome"] == nome_antigo:
            baralho["nome"] = nome_novo
            break
    with open(ARQUIVO_BARALHOS, "w", encoding="utf-8") as f:
        json.dump(baralhos, f, indent=4, ensure_ascii=False)

def deletar_baralho(nome_baralho):
    baralhos = carregar_baralhos()
    baralhos = [baralho for baralho in baralhos if baralho["nome"] != nome_baralho]
    with open(ARQUIVO_BARALHOS, "w", encoding="utf-8") as f:
        json.dump(baralhos, f, indent=4, ensure_ascii=False)

def salvar_cartao_em_baralho(nome_baralho, pergunta, resposta):
    baralhos = carregar_baralhos()
    for baralho in baralhos:
        if baralho["nome"] == nome_baralho:
            if "cartoes" not in baralho:
                baralho["cartoes"] = []
            baralho["cartoes"].append({"pergunta": pergunta, "resposta": resposta, "vezes_apareceu": 0, "vezes_acertou": 0})
            break
    with open(ARQUIVO_BARALHOS, "w", encoding="utf-8") as f:
        json.dump(baralhos, f, indent=4, ensure_ascii=False)

def salvar_editar_cartao(nome_baralho, cartao_original, nova_pergunta, nova_resposta):
    baralhos = carregar_baralhos()
    for baralho in baralhos:
        if baralho["nome"] == nome_baralho:
            for cartao in baralho["cartoes"]:
                if cartao == cartao_original:  # Encontrando o cartão original
                    cartao["pergunta"] = nova_pergunta
                    cartao["resposta"] = nova_resposta
                    break
            break
    with open(ARQUIVO_BARALHOS, "w", encoding="utf-8") as f:
        json.dump(baralhos, f, indent=4, ensure_ascii=False)

def atualizar_data_ultimo_estudo(nome_baralho):
    # Carregar os baralhos
    baralhos = carregar_baralhos()

    # Encontrar o baralho específico
    for baralho in baralhos:
        if baralho["nome"] == nome_baralho:
            # Atualizar a data de último estudo para a data atual
            baralho["data_ultimo_estudo"] = datetime.now().strftime("%Y-%m-%d")
            # Incrementar o número de vezes que o baralho foi estudado
            baralho["vezes_estudado"] += 1
            break

    # Salvar as alterações no arquivo JSON
    with open(ARQUIVO_BARALHOS, "w", encoding="utf-8") as f:
        json.dump(baralhos, f, indent=4, ensure_ascii=False)

def mostrar_tela_inicial():
    for widget in root.winfo_children():
        widget.destroy()

    titulo = tk.Label(root, text="Menu - Flashcard", font=("Helvetica", 18))
    titulo.pack(pady=10)

    botao_criar = tk.Button(root, text="Criar Baralho", font=("Helvetica", 14), command=mostrar_tela_criacao)
    botao_criar.pack(pady=5)

    baralhos = carregar_baralhos()
    total = len(baralhos)
    label_total = tk.Label(root, text=f"Total de baralhos: {total}", font=("Helvetica", 12))
    label_total.pack(pady=(0, 5))

    frame_principal = tk.Frame(root)
    frame_principal.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = tk.Canvas(frame_principal, height=200)
    scrollbar = tk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    baralhos = carregar_baralhos()
    if baralhos:
        for baralho in baralhos:
            nome = baralho["nome"]
            qtd_cartoes = len(baralho.get("cartoes", []))
            # Verifica se o baralho está com atraso (7 dias ou mais)
            icone_alerta = ""
            data_str = baralho.get("data_ultimo_estudo")
            if data_str:
                try:
                    data_estudo = datetime.strptime(data_str, "%Y-%m-%d")
                    if datetime.now() - data_estudo >= timedelta(days=7):
                        icone_alerta = " ⚠️"
                except ValueError:
                    pass
            else:
                try:
                    data_criacao = datetime.strptime(baralho.get("data_criacao", ""), "%Y-%m-%d")
                    if datetime.now() - data_criacao >= timedelta(days=7):
                        icone_alerta = " ⚠️"
                except ValueError:
                    icone_alerta = " ⚠️"  # caso a data esteja mal formatada
            texto_botao = f"{nome} ({qtd_cartoes} cartão{'s' if qtd_cartoes != 1 else ''}){icone_alerta}"

    
            btn = tk.Button(
                scrollable_frame,
                text=texto_botao,
                font=("Helvetica", 12),
                anchor="w",
                relief="flat",
                command=lambda nome=nome: mostrar_tela_baralho(nome)
            )
            btn.pack(fill="x", pady=2, padx=5)

            def on_enter(event, btn=btn):
                btn.config(bg="lightblue", cursor="hand2")

            def on_leave(event, btn=btn):
                btn.config(bg=btn.original_bg, cursor="arrow")

            btn.original_bg = btn.cget("bg")
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
    else:
        label = tk.Label(scrollable_frame, text="Nenhum baralho criado ainda.", font=("Helvetica", 12))
        label.pack()

def mostrar_tela_criacao():
    for widget in root.winfo_children():
        widget.destroy()

    titulo = tk.Label(root, text="Criar Novo Baralho", font=("Helvetica", 18))
    titulo.pack(pady=20)

    label_nome = tk.Label(root, text="Nome do Baralho:")
    label_nome.pack()
    entrada_nome = tk.Entry(root, width=40)
    entrada_nome.pack(pady=5)

    def salvar_baralho():
        nome = entrada_nome.get().strip()
        if nome:
            salvar_novo_baralho(nome)
            mostrar_tela_inicial()
        else:
            print("Nome do baralho não pode estar vazio.")

    botao_salvar = tk.Button(root, text="Salvar Baralho", command=salvar_baralho)
    botao_salvar.pack(pady=10)

    botao_voltar = tk.Button(root, text="Voltar", command=mostrar_tela_inicial)
    botao_voltar.pack(pady=5)

def mostrar_tela_baralho(nome_baralho):
    # Limpa a tela atual
    for widget in root.winfo_children():
        widget.destroy()

    # Título da tela
    titulo = tk.Label(root, text=f"Baralho: {nome_baralho}", font=("Helvetica", 18))
    titulo.pack(pady=20)

    # Carregar os baralhos e procurar o baralho selecionado
    baralhos = carregar_baralhos()
    baralho_atual = None
    for baralho in baralhos:
        if baralho["nome"] == nome_baralho:
            baralho_atual = baralho
            break

    # Exibindo as informações do baralho
    if baralho_atual:
        data_criacao = baralho_atual.get("data_criacao", "Desconhecido")
        data_ultimo_estudo = baralho_atual.get("data_ultimo_estudo", "Nunca")
        vezes_estudado = baralho_atual.get("vezes_estudado", 0)
        total_cartoes = len(baralho_atual.get("cartoes", [])) 

        label_total_cartoes = tk.Label(root, text=f"Total de Cartões: {total_cartoes}", font=("Helvetica", 8))
        label_total_cartoes.pack(padx=3, pady=5, anchor="w")

        label_data_criacao = tk.Label(root, text=f"Data de Criação: {data_criacao}", font=("Helvetica", 8))
        label_data_criacao.pack(padx=3, pady=5,anchor="w")

        label_data_ultimo_estudo = tk.Label(root, text=f"Data do Último Estudo: {data_ultimo_estudo}", font=("Helvetica", 8))
        label_data_ultimo_estudo.pack(padx=3, pady=5,anchor="w")

        label_vezes_estudado = tk.Label(root, text=f"Vezes Estudados: {vezes_estudado}", font=("Helvetica", 8))
        label_vezes_estudado.pack(padx=3, pady=5,anchor="w")

    # Se o baralho estiver vazio, exibe uma mensagem e não cria o botão "ESTUDAR"
    if not baralho_atual or not baralho_atual.get("cartoes"):
        label_vazio = tk.Label(root, text="Este baralho está vazio. Adicione cartões para estudar.", font=("Helvetica", 12))
        label_vazio.pack(pady=10)
        botao_estudar = None  # Não cria o botão "ESTUDAR" se não houver cartões
    else:
        # Adiciona o botão "ESTUDAR"
        botao_estudar = tk.Button(
            root, text="ESTUDAR", font=("Helvetica", 12), width=20, height=2,
            command=lambda: [atualizar_data_ultimo_estudo(nome_baralho), mostrar_tela_estudo(nome_baralho)]
        )
        botao_estudar.pack(pady=10)  # Botão "ESTUDAR"

    # Botão para criar novo cartão
    botao_criar_cartao = tk.Button(
        root, text="Criar Cartão", font=("Helvetica", 10), width=10, height=1, command=lambda: mostrar_tela_cartao(nome_baralho)
    )
    botao_criar_cartao.pack(pady=5)

    # Frame para conter o canvas e a scrollbar
    frame_cartoes = tk.Frame(root)
    frame_cartoes.pack(pady=10, padx=10, fill="both", expand=True)

    # Canvas e Scrollbar
    canvas = tk.Canvas(frame_cartoes)
    scrollbar = tk.Scrollbar(frame_cartoes, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Frame para os cartões dentro do canvas
    scrollable_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Configuração de scrollbar
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Exibição do canvas e da scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Função para rolar a tela com o mouse
    def on_mousewheel(event):
        if canvas.winfo_ismapped():  # Verifica se o canvas está visível
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # Registra o evento de rolagem no canvas
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # Preencher com cartões
    if baralho_atual and baralho_atual.get("cartoes"):
        for i, cartao in enumerate(baralho_atual["cartoes"], 1):
            texto_cartao = f"{i}. Q: {cartao['pergunta']}  |  R: {cartao['resposta']}"

            # Cria o label para exibir o cartão
            label_cartao = tk.Label(scrollable_frame, text=texto_cartao, anchor="w", justify="left", wraplength=350)
            label_cartao.pack(fill="x", pady=2)

            def on_enter(event, label=label_cartao):
                label.config(bg="lightblue", cursor="hand2")

            def on_leave(event, label=label_cartao):
                label.config(bg=label_cartao.original_bg, cursor="arrow")

            label_cartao.original_bg = label_cartao.cget("bg")
            label_cartao.bind("<Enter>", on_enter)
            label_cartao.bind("<Leave>", on_leave)

            label_cartao.bind("<Button-1>", lambda event, cartao=cartao: mostrar_tela_editar_cartao(nome_baralho, cartao))
    else:
        label_vazio = tk.Label(scrollable_frame, text="Nenhum cartão neste baralho ainda.", font=("Helvetica", 10))
        label_vazio.pack()

    frame_botoes = tk.Frame(root)
    frame_botoes.pack(pady=10)

    # Botões de deletar e renomear baralho
    botao_deletar = tk.Button(
        frame_botoes, text="Deletar", font=("Helvetica", 10), fg="red", width=10, height=1,
        command=lambda nome=nome_baralho: deletar_baralho(nome) or mostrar_tela_inicial()
    )
    botao_renomear = tk.Button(
        frame_botoes, text="Renomear", font=("Helvetica", 10), fg="blue", width=10, height=1,
        command=lambda nome=nome_baralho: mostrar_tela_renomear(nome)
    )

    # Exibição dos botões
    botao_deletar.grid(row=0, column=0, padx=10)
    botao_renomear.grid(row=0, column=1, padx=10)
    botao_voltar = tk.Button(frame_botoes, text="Voltar", command=mostrar_tela_inicial)
    botao_voltar.grid(row=0, column=2, padx=10)

def mostrar_tela_cartao(nome_baralho):
    for widget in root.winfo_children():
        widget.destroy()

    titulo = tk.Label(root, text=f"Cartão - {nome_baralho}", font=("Helvetica", 18))
    titulo.pack(pady=10)

    label_pergunta = tk.Label(root, text="Pergunta:")
    label_pergunta.pack()
    entrada_pergunta = tk.Entry(root, width=40)
    entrada_pergunta.pack(pady=5)

    label_resposta = tk.Label(root, text="Resposta:")
    label_resposta.pack()
    entrada_resposta = tk.Entry(root, width=40)
    entrada_resposta.pack(pady=5)

    def salvar_cartao():
        pergunta = entrada_pergunta.get().strip()
        resposta = entrada_resposta.get().strip()
        if pergunta and resposta:
            salvar_cartao_em_baralho(nome_baralho, pergunta, resposta)
            entrada_pergunta.delete(0, tk.END)
            entrada_resposta.delete(0, tk.END)
            print("Cartão salvo com sucesso!")
        else:
            print("Preencha os dois campos!")

    botao_salvar = tk.Button(root, text="Salvar Cartão", command=salvar_cartao)
    botao_salvar.pack(pady=10)

    botao_voltar = tk.Button(root, text="Voltar", command=lambda: mostrar_tela_baralho(nome_baralho))
    botao_voltar.pack(pady=5)

def mostrar_tela_editar_cartao(nome_baralho, cartao):
    for widget in root.winfo_children():
        widget.destroy()

    titulo = tk.Label(root, text=f"Editar Cartão - {nome_baralho}", font=("Helvetica", 18))
    titulo.pack(pady=10)

    label_pergunta = tk.Label(root, text="Pergunta:")
    label_pergunta.pack()
    entrada_pergunta = tk.Entry(root, width=40)
    entrada_pergunta.insert(0, cartao["pergunta"])  # Preenche o campo com a pergunta atual
    entrada_pergunta.pack(pady=5)

    label_resposta = tk.Label(root, text="Resposta:")
    label_resposta.pack()
    entrada_resposta = tk.Entry(root, width=40)
    entrada_resposta.insert(0, cartao["resposta"])  # Preenche o campo com a resposta atual
    entrada_resposta.pack(pady=5)

    # Adiciona as informações de uso do cartão
    label_vezes_apareceu = tk.Label(root, text=f"Vezes que o cartão apareceu: {cartao['vezes_apareceu']}")
    label_vezes_apareceu.pack()

    label_vezes_acertou = tk.Label(root, text=f"Vezes que o usuário acertou: {cartao['vezes_acertou']}")
    label_vezes_acertou.pack()

    # Calcula a taxa de acerto e a exibe com 2 dígitos
    if cartao['vezes_apareceu'] > 0:
        taxa_acerto = (cartao['vezes_acertou'] / cartao['vezes_apareceu']) * 100
        label_taxa_acerto = tk.Label(root, text=f"Taxa de acerto: {taxa_acerto:.0f}%")
        label_taxa_acerto.pack()
    else:
        label_taxa_acerto = tk.Label(root, text="Taxa de acerto: 0.00%")
        label_taxa_acerto.pack()

    def salvar_cartao_editado():
        pergunta = entrada_pergunta.get().strip()
        resposta = entrada_resposta.get().strip()
        if pergunta and resposta:
            # Salva a edição do cartão
            salvar_editar_cartao(nome_baralho, cartao, pergunta, resposta)
            mostrar_tela_baralho(nome_baralho)  # Volta para a tela do baralho
        else:
            print("Preencha os dois campos!")

    def deletar_cartao():
        deletar_cartao_em_baralho(nome_baralho, cartao)
        mostrar_tela_baralho(nome_baralho)  # Volta para a tela do baralho

    botao_salvar = tk.Button(root, text="Salvar Alterações", command=salvar_cartao_editado)
    botao_salvar.pack(pady=10)

    botao_deletar = tk.Button(root, text="Deletar Cartão", fg="red", command=deletar_cartao)
    botao_deletar.pack(pady=5)

    botao_voltar = tk.Button(root, text="Voltar", command=lambda: mostrar_tela_baralho(nome_baralho))
    botao_voltar.pack(pady=5)

def deletar_cartao_em_baralho(nome_baralho, cartao):
    baralhos = carregar_baralhos()
    for baralho in baralhos:
        if baralho["nome"] == nome_baralho:
            baralho["cartoes"] = [c for c in baralho["cartoes"] if c != cartao]  # Remove o cartão
            break
    with open(ARQUIVO_BARALHOS, "w", encoding="utf-8") as f:
        json.dump(baralhos, f, indent=4, ensure_ascii=False)

def mostrar_tela_renomear(nome_baralho):
    for widget in root.winfo_children():
        widget.destroy()

    titulo = tk.Label(root, text=f"Renomear Baralho: {nome_baralho}", font=("Helvetica", 18))
    titulo.pack(pady=20)

    label_nome_atual = tk.Label(root, text=f"Nome Atual: {nome_baralho}", font=("Helvetica", 12))
    label_nome_atual.pack(pady=10)

    label_novo_nome = tk.Label(root, text="Novo Nome do Baralho:")
    label_novo_nome.pack()

    entrada_novo_nome = tk.Entry(root, width=40)
    entrada_novo_nome.pack(pady=5)

    def trocar_nome():
        novo_nome = entrada_novo_nome.get().strip()
        if novo_nome:
            salvar_renomear_baralho(nome_baralho, novo_nome)
            mostrar_tela_baralho(novo_nome)

    botao_trocar_nome = tk.Button(root, text="Trocar Nome", command=trocar_nome)
    botao_trocar_nome.pack(pady=10)

    botao_voltar = tk.Button(root, text="Voltar", command=mostrar_tela_inicial)
    botao_voltar.pack(pady=5)

# Função para exibir a tela de estudo
def mostrar_tela_estudo(nome_baralho):
    for widget in root.winfo_children():
        widget.destroy()

    baralhos = carregar_baralhos()
    baralho_atual = None

    for baralho in baralhos:
        if baralho["nome"] == nome_baralho:
            baralho_atual = baralho
            break

    if not baralho_atual or "cartoes" not in baralho_atual or len(baralho_atual["cartoes"]) == 0:
        tk.Label(root, text="Não há cartões para estudar.", font=("Helvetica", 14)).pack(pady=20)
        return

    cartoes = baralho_atual["cartoes"]
    random.shuffle(cartoes)

    indice_cartao = [0]

    def salvar_baralhos():
        with open("baralhos.json", "w", encoding="utf-8") as f:
            json.dump(baralhos, f, indent=4, ensure_ascii=False)

    def mostrar_proximo_cartao():
        if indice_cartao[0] < len(cartoes):
            cartao = cartoes[indice_cartao[0]]

            # Incrementa vezes_apareceu
            if "vezes_apareceu" not in cartao:
                cartao["vezes_apareceu"] = 0
            cartao["vezes_apareceu"] += 1
            salvar_baralhos()

            pergunta_label.config(text=cartao["pergunta"])
            resposta_label.config(text="")

            botao_acertou.pack_forget()
            botao_errou.pack_forget()
            botao_mostrar_resposta.pack(pady=10)
        else:
            pergunta_label.config(text="Parabéns! Estudo concluído.")
            resposta_label.config(text="")
            botao_acertou.pack_forget()
            botao_errou.pack_forget()
            botao_encerrar_estudo.pack(pady=10)

    def mostrar_resposta():
        if indice_cartao[0] < len(cartoes):
            cartao = cartoes[indice_cartao[0]]
            resposta_label.config(text=cartao["resposta"])
            botao_mostrar_resposta.pack_forget()
            botao_acertou.pack(pady=5)
            botao_errou.pack(pady=5)

    def marcar_como_acertado():
        cartao = cartoes[indice_cartao[0]]
        if "vezes_acertou" not in cartao:
            cartao["vezes_acertou"] = 0
        cartao["vezes_acertou"] += 1
        salvar_baralhos()
        indice_cartao[0] += 1
        mostrar_proximo_cartao()

    def marcar_como_errado():
        indice_cartao[0] += 1
        mostrar_proximo_cartao()

    def encerrar_estudo():
        mostrar_tela_baralho(nome_baralho)

    titulo = tk.Label(root, text=f"Estudo do Baralho: {nome_baralho}", font=("Helvetica", 18))
    titulo.pack(pady=20)

    botao_encerrar_estudo = tk.Button(root, text="ENCERRAR ESTUDO", font=("Helvetica", 12), command=encerrar_estudo, bg="red", fg="white")
    botao_encerrar_estudo.pack(pady=10)

    pergunta_label = tk.Label(root, text="", font=("Helvetica", 12), wraplength=350, justify="left")
    pergunta_label.pack(padx=10, pady=10)

    resposta_label = tk.Label(root, text="", font=("Helvetica", 14), fg="green")
    resposta_label.pack(pady=10)

    botao_mostrar_resposta = tk.Button(root, text="MOSTRAR RESPOSTA", font=("Helvetica", 12), command=mostrar_resposta)
    botao_acertou = tk.Button(root, text="ACERTEI", font=("Helvetica", 12), bg="green", fg="white", command=marcar_como_acertado)
    botao_errou = tk.Button(root, text="ERREI", font=("Helvetica", 12), bg="red", fg="white", command=marcar_como_errado)

    mostrar_proximo_cartao()

root = tk.Tk()
root.title("Protótipo Flashcard")
root.geometry("400x800")

mostrar_tela_inicial()
root.mainloop()