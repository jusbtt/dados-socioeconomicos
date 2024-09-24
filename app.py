from flask import Flask, render_template, request, redirect
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

data_file = 'data/dados_socioeconomicos.csv'

def load_data():
    return pd.read_csv(data_file)

@app.route('/')
def index():
    dados = load_data()
    dados_ordenados = dados.sort_values(by='Nome')
    dados_ordenados['Renda Mensal'] = dados_ordenados['Renda Mensal'].apply(lambda x: f'R$ {str(x).replace(".", ",")}')
    total_registros = len(dados_ordenados)
    return render_template('index.html', dados=dados_ordenados.to_dict(orient='records'), total=total_registros)

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    dados = load_data()
    dados = dados[dados['ID'] != id]
    dados.to_csv(data_file, index=False)
    return redirect('/')

@app.route('/adicionar', methods=['POST'])
def adicionar():
    dados = load_data()
    novo_registro = {
        'ID': dados['ID'].max() + 1,
        'Nome': request.form['nome'],
        'Idade': request.form['idade'],
        'Gênero': request.form['genero'],
        'Renda Mensal': float(request.form['renda'].replace(',', '.')),
        'Nível de Escolaridade': request.form['escolaridade'],
        'Ocupação': request.form['ocupacao'],
        'Categoria que precisa de melhora': request.form['categoria'],
        'Número de Dependentes': request.form['dependentes'],
        'Tempo de Residência': request.form['tempo'],
        'Acesso à Internet': request.form['internet'],
        'Data do Registro': request.form['data']
    }

    novo_registro_df = pd.DataFrame([novo_registro])
    dados = pd.concat([dados, novo_registro_df], ignore_index=True)
    dados.to_csv(data_file, index=False)
    return redirect('/')

@app.route('/grafico')
def grafico_categorias(dados):
    conteagem_categorias = dados['Categoria que precisa de melhora'].value_counts()
    
    plt.figure(figsize=(8, 6))
    plt.pie(conteagem_categorias, labels=conteagem_categorias.index, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Para garantir que o gráfico seja um círculo
    plt.title('Distribuição das Categorias que Precisam de Melhora')
    
    plt.savefig(os.path.join('static', 'grafico.png'))
    plt.close()
    
    return redirect('/')

@app.route('/filtrar', methods=['POST'])
def filtrar():
    categoria = request.form.get('categoria')
    faixa_etaria = request.form.get('faixa_etaria')
    faixa_salario = request.form.get('faixa_salario')
    escolaridade = request.form.get('escolaridade')

    # Lógica para filtrar os dados
    dados_filtrados = load_data()

    if categoria and categoria != "":
        dados_filtrados = dados_filtrados[dados_filtrados['Categoria que precisa de melhora'] == categoria]
    
    if faixa_etaria and faixa_etaria != "":
        if faixa_etaria == '0-17':
            dados_filtrados = dados_filtrados[dados_filtrados['Idade'] <= 17]
        elif faixa_etaria == '18-30':
            dados_filtrados = dados_filtrados[(dados_filtrados['Idade'] >= 18) & (dados_filtrados['Idade'] <= 30)]
        elif faixa_etaria == '31-50':
            dados_filtrados = dados_filtrados[(dados_filtrados['Idade'] >= 31) & (dados_filtrados['Idade'] <= 50)]
        elif faixa_etaria == '51+':
            dados_filtrados = dados_filtrados[dados_filtrados['Idade'] > 50]

    if faixa_salario and faixa_salario != "":
        # Converter 'Renda Mensal' para float para comparação
        dados_filtrados['Renda Mensal'] = dados_filtrados['Renda Mensal'].astype(float)

        if faixa_salario == '0-1500':
            dados_filtrados = dados_filtrados[dados_filtrados['Renda Mensal'] <= 1500]
        elif faixa_salario == '1501-3000':
            dados_filtrados = dados_filtrados[(dados_filtrados['Renda Mensal'] > 1500) & (dados_filtrados['Renda Mensal'] <= 3000)]
        elif faixa_salario == '3001-4500':
            dados_filtrados = dados_filtrados[(dados_filtrados['Renda Mensal'] > 3000) & (dados_filtrados['Renda Mensal'] <= 4500)]
        elif faixa_salario == '4501+':
            dados_filtrados = dados_filtrados[dados_filtrados['Renda Mensal'] > 4500]

    if escolaridade and escolaridade != "":
        dados_filtrados = dados_filtrados[dados_filtrados['Nível de Escolaridade'] == escolaridade]

    # Gerar gráfico com os dados filtrados
    grafico_categorias(dados_filtrados)

    total = dados_filtrados.shape[0]
    return render_template('index.html', dados=dados_filtrados.to_dict(orient='records'), total=total)

@app.route('/resetar', methods=['POST'])
def resetar():
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
