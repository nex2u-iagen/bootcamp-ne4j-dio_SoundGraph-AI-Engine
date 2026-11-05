# ==============================================================================
# SCRIPT DE COLETA AUTOMATIZADA - DATASET KAGGLE 2026
# ==============================================================================

# 'import' carrega módulos da biblioteca padrão e de terceiros
import os        # 'os': Permite navegar por pastas e arquivos do sistema operacional
import shutil    # 'shutil': Utilitários para copiar ou mover arquivos fisicamente
import kagglehub # 'kagglehub': Biblioteca do Kaggle para baixar datasets direto via código

print("⏳ [1/3] Conectando ao Kaggle e baixando o dataset...")

# Baixa a versão mais recente do dataset 'uditjain13/music-streaming-habits-2026'
caminho_cache = kagglehub.dataset_download("uditjain13/music-streaming-habits-2026")
print(f"✔️ Arquivos baixados no cache local: {caminho_cache}")

# Varre a pasta de cache para encontrar o arquivo CSV baixado
arquivos = [f for f in os.listdir(caminho_cache) if f.endswith(".csv")]

if arquivos:
    arquivo_origem = os.path.join(caminho_cache, arquivos[0])

    # Define o caminho de destino dentro da pasta 'import' que o Neo4j enxerga
    arquivo_destino = os.path.join("import", "musicas.csv")

    print(f"⏳ [2/3] Copiando o arquivo para {arquivo_destino}...")
    shutil.copy(arquivo_origem, arquivo_destino)

    # Concede permissão total de leitura no arquivo CSV para o container Docker
    os.chmod(arquivo_destino, 0o777)

    print("✅ [3/3] Arquivo 'musicas.csv' pronto dentro da pasta import!")
else:
    print("❌ Erro: Nenhum arquivo CSV encontrado na pasta baixada.")
