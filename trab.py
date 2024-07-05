from collections import deque
from datetime import datetime

class ItemCardapio:
    def __init__(self, nome, preco):
        self.nome = nome
        self.preco = preco

class Pedido:
    def __init__(self, numero_mesa, itens):
        self.numero_mesa = numero_mesa
        self.itens = itens
        self.hora_pedido = datetime.now()
        self.status = 'Pedido'  

class GerenciadorPedidos:
    def __init__(self):
        self.pedidos = deque()
        self.preparacao = deque()
        self.entregues = []
        self.janelas = []

    def adicionar_janela(self, janela):
        self.janelas.append(janela)

    def atualizar_janelas(self):
        for janela in self.janelas:
            janela.atualizar_lista_pedidos()

    def adicionar_pedido(self, pedido):
        self.pedidos.append(pedido)
        self.atualizar_janelas()

    def iniciar_preparacao(self):
        if self.pedidos:
            pedido = self.pedidos.popleft()
            pedido.status = 'Em preparação'
            self.preparacao.append(pedido)
        self.atualizar_janelas()

    def finalizar_preparacao(self):
        if self.preparacao:
            pedido = self.preparacao.popleft()
            pedido.status = 'Entregue'
            self.entregues.append(pedido)
        self.atualizar_janelas()

    def relatorio_faturamento(self):
        total_faturamento = 0
        itens_vendidos = {}
        for pedido in self.entregues:
            for item in pedido.itens:
                total_faturamento += item.preco
                if item.nome in itens_vendidos:
                    itens_vendidos[item.nome] += 1
                else:
                    itens_vendidos[item.nome] = 1
        return total_faturamento, itens_vendidos

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QSpinBox, QListWidget, QMessageBox

class JanelaAtendente(QMainWindow):
    def __init__(self, gerenciador_pedidos, cardapio):
        super().__init__()
        self.gerenciador_pedidos = gerenciador_pedidos
        self.cardapio = cardapio
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Atendente')
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        self.mesa_input = QLineEdit(self)
        self.mesa_input.setPlaceholderText('Número da Mesa')
        layout.addWidget(self.mesa_input)
        
        self.itens_layout = QVBoxLayout()
        self.itens_inputs = []
        for item in self.cardapio:
            h_layout = QHBoxLayout()
            label = QLabel(f'{item.nome} - R${item.preco:.2f}', self)
            spin_box = QSpinBox(self)
            spin_box.setRange(0, 20)
            h_layout.addWidget(label)
            h_layout.addWidget(spin_box)
            self.itens_inputs.append((item, spin_box))
            self.itens_layout.addLayout(h_layout)
        
        layout.addLayout(self.itens_layout)
        
        self.btn_adicionar = QPushButton('Adicionar Pedido', self)
        self.btn_adicionar.clicked.connect(self.adicionar_pedido)
        layout.addWidget(self.btn_adicionar)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def adicionar_pedido(self):
        numero_mesa = self.mesa_input.text()
        if not numero_mesa:
            QMessageBox.warning(self, 'Erro', 'Número da mesa não pode ser vazio.')
            return
        
        itens_pedido = []
        for item, spin_box in self.itens_inputs:
            quantidade = spin_box.value()
            if quantidade > 0:
                for _ in range(quantidade):
                    itens_pedido.append(item)
        
        if not itens_pedido:
            QMessageBox.warning(self, 'Erro', 'Selecione pelo menos um item.')
            return
        
        pedido = Pedido(numero_mesa, itens_pedido)
        self.gerenciador_pedidos.adicionar_pedido(pedido)
        QMessageBox.information(self, 'Sucesso', 'Pedido adicionado com sucesso.')
        self.mesa_input.clear()
        for _, spin_box in self.itens_inputs:
            spin_box.setValue(0)
        
        # Atualizar lista de pedidos na cozinha
        self.gerenciador_pedidos.atualizar_janelas()

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QListWidget, QWidget

class JanelaCozinha(QMainWindow):
    def __init__(self, gerenciador_pedidos):
        super().__init__()
        self.gerenciador_pedidos = gerenciador_pedidos
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Cozinha')
        self.setGeometry(500, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        self.lista_pedidos = QListWidget(self)
        layout.addWidget(self.lista_pedidos)
        
        self.btn_iniciar_preparacao = QPushButton('Iniciar Preparação', self)
        self.btn_iniciar_preparacao.clicked.connect(self.iniciar_preparacao)
        layout.addWidget(self.btn_iniciar_preparacao)
        
        self.btn_finalizar_preparacao = QPushButton('Finalizar Preparação', self)
        self.btn_finalizar_preparacao.clicked.connect(self.finalizar_preparacao)
        layout.addWidget(self.btn_finalizar_preparacao)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.atualizar_lista_pedidos()
    
    def atualizar_lista_pedidos(self):
        self.lista_pedidos.clear()
        for pedido in self.gerenciador_pedidos.pedidos:
            self.lista_pedidos.addItem(f'Mesa {pedido.numero_mesa} - {pedido.status}')
        for pedido in self.gerenciador_pedidos.preparacao:
            self.lista_pedidos.addItem(f'Mesa {pedido.numero_mesa} - {pedido.status}')
    
    def iniciar_preparacao(self):
        self.gerenciador_pedidos.iniciar_preparacao()
        self.atualizar_lista_pedidos()
    
    def finalizar_preparacao(self):
        self.gerenciador_pedidos.finalizar_preparacao()
        self.atualizar_lista_pedidos()

class JanelaRelatorio(QMainWindow):
    def __init__(self, gerenciador_pedidos):
        super().__init__()
        self.gerenciador_pedidos = gerenciador_pedidos
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Relatório')
        self.setGeometry(100, 500, 400, 300)
        
        layout = QVBoxLayout()
        
        self.label_faturamento = QLabel('Faturamento Total: R$0.00', self)
        layout.addWidget(self.label_faturamento)
        
        self.label_itens_vendidos = QLabel('Itens Vendidos:', self)
        layout.addWidget(self.label_itens_vendidos)
        
        self.lista_itens_vendidos = QListWidget(self)
        layout.addWidget(self.lista_itens_vendidos)
        
        self.btn_atualizar = QPushButton('Atualizar Relatório', self)
        self.btn_atualizar.clicked.connect(self.atualizar_relatorio)
        layout.addWidget(self.btn_atualizar)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.atualizar_relatorio()
    
    def atualizar_relatorio(self):
        total_faturamento, itens_vendidos = self.gerenciador_pedidos.relatorio_faturamento()
        self.label_faturamento.setText(f'Faturamento Total: R${total_faturamento:.2f}')
        self.lista_itens_vendidos.clear()
        for item, quantidade in itens_vendidos.items():
            self.lista_itens_vendidos.addItem(f'{item}: {quantidade}')
    
    def atualizar_lista_pedidos(self):
        pass

class Aplicacao(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.gerenciador_pedidos = GerenciadorPedidos()
        self.cardapio = [
            ItemCardapio('Hambúrguer', 10.0),
            ItemCardapio('Pizza', 20.0),
            ItemCardapio('Refrigerante', 5.0)
        ]
        self.janela_atendente = JanelaAtendente(self.gerenciador_pedidos, self.cardapio)
        self.janela_cozinha = JanelaCozinha(self.gerenciador_pedidos)
        self.janela_relatorio = JanelaRelatorio(self.gerenciador_pedidos)
    
        self.gerenciador_pedidos.adicionar_janela(self.janela_cozinha)
    
    def start(self):
        self.janela_atendente.show()
        self.janela_cozinha.show()
        self.janela_relatorio.show()

if __name__ == '__main__':
    app = Aplicacao(sys.argv)
    app.start()
    sys.exit(app.exec_())