# Importa utils
import pandas as pd 
import random
from datetime import datetime, timedelta
import logging 
import sys

# Configura o logger
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Função para geração de dados
def generate_data(target_rows:int = 6641):
    """
    Generates a 20 thousand row supermarket sales dataset with the following columns:
        'Invoice ID': unique invoice ID,
        'Date': transaction date,
        'City': supermarket branch,
        'Gender': customer gender,
        'Customer type': normal | member,
        'Product line': product category (food, health, etc.),
        'Payment': payment method (credit, debit, cash, etc.),
        'Unit price': product unitary price,
        'Quantity': transaction product amount,
        'Total': Unit price * Quantity,
        'Gross margin percentage': gross margin percentage,
        'Gross income': total (total revenue + tax) * gross margin percentage,
        'Rating': Supermarket rating
    
    :param target_rows: Target number of rows.
    :type target_rows: int
    """

    # Tenta carregar o dataset e atribuir colunas às variáveis
    try:
        df = pd.read_csv("data/supermarket_sales.csv", sep=';', decimal=',')
        cities = df["City"].unique()
        customer_type = df["Customer type"].unique()
        gender = df["Gender"].unique()
        payment = df['Payment'].unique()
    except Exception as e:
        logger.error(f"Error reading CSV base: {e}")
        sys.exit()

    # Define os pesos das Filiais
    branch_weights = {
        "Mandalay": 30,
        "Naypyitaw": 15,
        "Yangon": 55
    }

    payment_method_weights = {
        "Ewallet": 40,
        "Credit card": 45,
        "Cash": 15
    }

    # Define os pesos que os produtos tem em proporção
    product_weights = {
        "Food and beverages": 50,     
        "Health and beauty": 15,
        "Sports and travel": 5,
        "Home and lifestyle": 15,
        "Electronic accessories": 5, 
        "Fashion accessories": 10
    }

    # Define o range de preços por categoria de produtos
    price_ranges = {
        "Food and beverages": (5, 100),     
        "Health and beauty": (10, 300),
        "Sports and travel": (30, 350),
        "Home and lifestyle": (5, 500),
        "Electronic accessories": (50, 800), 
        "Fashion accessories": (20, 300)
    }

    # Cria as listas das categorias e pesos 
    products_list = list(product_weights.keys())
    products_weights_list = list(product_weights.values())

    branches_list = list(branch_weights.keys())
    branches_weights_list = list(branch_weights.values())

    payment_method_list = list(payment_method_weights.keys())
    payment_method__list = list(payment_method_weights.values())

    # Define a lista de categorias de produtos com pesos
    weighted_products_list = random.choices(products_list, weights=products_weights_list, k=target_rows)
    weighted_payment_methods_list = random.choices(payment_method_list, weights=payment_method__list, k=target_rows)
    weighted_branches_list= random.choices(branches_list, weights=branches_weights_list, k=target_rows)

    # Data de início
    start_date = datetime.strptime("01/01/2026", "%d/%m/%Y")

    # Lista em que os dados novos serão armazenados
    new_data = []

    logger.info(f"Generating dataset with {target_rows} rows.")

    # Tenta gerar um novo registro com base nas guidelines
    try:
        for i in range(target_rows):
            # últimos 5 anos
            days = random.randint(0, 364)

            # duração do dataset
            duration = timedelta(days=days)

            # produto atual definido como um produto com peso
            current_product = weighted_products_list[i]
            current_payment_method = weighted_payment_methods_list[i]
            current_branch = weighted_branches_list[i]

            # preços mínimos e máximos com base na guideline
            min_price, max_price = price_ranges[current_product]

            # simula o crescimento das vendas
            quantity_growth = int(days / 600) * 1 
            quantity = random.randint(1, 10) + quantity_growth

            # simula o impacto da inflação
            price_inflation = int(days / 365) * 5
            price = random.randint(min_price, max_price) + price_inflation

            # faturamento, percentual de lucro e lucro 
            total = (price * quantity) * 1.05
            gross_margin_percentage = 0.0479 # 4.8%
            gross_income = total * gross_margin_percentage

            # data atual = inicio + duração
            actual_date = start_date + duration

            # linha a ser gerada
            row = {
                'Invoice ID': f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(100,999)}",
                'Date': actual_date,
                'City': current_branch,
                'Gender': random.choice(gender),
                'Customer type': random.choice(customer_type),
                'Product line': current_product,
                'Payment': current_payment_method,
                'Unit price': round(price, 2),
                'Quantity': quantity,
                'Total': round(total, 2),
                'Gross margin percentage': gross_margin_percentage,
                'Gross income': round(gross_income, 2),
                'Rating': round(random.uniform(1, 10),1)
            }
            
            # adiciona a linha à lista new_data
            new_data.append(row)
    except Exception as e:
        logger.error(f"Error while generating DataFrame rows: {e}")
        sys.exit()

    # Define o caminho do arquivo e armazena o novo datset
    file_path = "data/supermarket_sales_extended.csv"
    df_final = pd.DataFrame(new_data)
    df_final.to_csv(file_path, index=False, sep=';', decimal=',')

    logger.info(f"DataFrame with {target_rows} rows generated with success at the path: '{file_path}'.")

# Executa o script
if __name__ == "__main__":
    generate_data()
