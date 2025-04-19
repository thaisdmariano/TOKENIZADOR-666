import streamlit as st
import re
from unidecode import unidecode
from pymongo import MongoClient

# Conexão com o MongoDB
client = MongoClient("mongodb://localhost:27017/GENESYS")  # Conexão com o banco de dados GENESYS
db = client["GENESYS"]  # Nome do banco de dados
# Coleções
treinamento_collection = db["Treinamento_Tokenizado"]
teste_collection = db["Teste_Tokenizado"]

# Variável global para armazenar o índice atual
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0

def tokenize_text(text):
    words = text.split()
    if len(words) > 800:
        raise ValueError("O texto deve ter no máximo 800 palavras.")

    tokens = re.findall(r'\b\w+[\w(),]*\b', text)
    tokens = [unidecode(token) for token in tokens]
    return tokens

# Configuração da interface Streamlit
st.set_page_config(page_title="Tokenizador de Texto", page_icon="✂️", layout="wide")

st.title("🌟 Tokenizador de Texto 🌟")
st.write("Digite seu texto (até 800 palavras) e clique em 'Tokenizar' para ver as palavras separadas.")

# Criação de colunas para layout
col1, col2 = st.columns([2, 1])

with col1:
    input_text = st.text_area("Texto de entrada", height=300)

with col2:
    st.write("### Instruções:")
    st.write("1. Insira seu texto na caixa acima.")
    st.write("2. Escolha onde salvar os dados.")
    st.write("3. Clique no botão 'Tokenizar'.")
    st.write("4. Veja as palavras tokenizadas abaixo.")

# Opção para escolher a coleção
collection_choice = st.selectbox("Escolha a coleção para salvar os tokens:",
                                   ["Treinamento_Tokenizado", "Teste_Tokenizado"])

if st.button("Tokenizar"):
    try:
        tokens = tokenize_text(input_text)
        if tokens:
            # Atualiza o índice atual
            token_dict = {str(st.session_state.current_index + i): f'"{token}"' for i, token in enumerate(tokens)}
            st.session_state.current_index += len(tokens)  # Atualiza o índice para a próxima tokenização

            # Armazena a tokenização na coleção escolhida
            if collection_choice == "Treinamento_Tokenizado":
                treinamento_collection.insert_one({
                    "tokens": token_dict,
                    "timestamp": st.session_state.current_index
                })
            else:
                teste_collection.insert_one({
                    "tokens": token_dict,
                    "timestamp": st.session_state.current_index
                })

            st.write("### Palavras tokenizadas:")
            st.write(token_dict)
    except ValueError as e:
        st.error(e)
    except Exception as e:
        st.error(f"Ocorreu um erro ao salvar os dados: {e}")