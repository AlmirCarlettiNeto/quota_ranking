import pandas as pd

'''
Apenas documentando o material do edital

Tabela para discriminar o número de vagas

| Área       | Total | Pessoas com Deficiência (PcD) | Negros | Indígenas |
|------------|-------|-------------------------------|--------|-----------|
| Dev. Sist. | 285   | 44                            | 88     | 22        |


8.2. Se na aplicação dos percentuais de 20% (vinte por cento) para negros e 5% (cinco por cento) pra indígenas do
total de vagas criadas para cada cargo/especialidade resultar número fracionado, este será aumentado para o
primeiro número inteiro subsequente, em caso de fração igual ou maior que 0,5 (cinco décimos); ou diminuídos
para número inteiro imediatamente inferior, em caso de fração menor que 0,5 (cinco décimos).

8.2.1. A convocação dos candidatos que se declararem negros deverá obedecer ao seguinte critério: a primeira
contratação ocorrerá na 3ª (terceira) vaga a ser preenchida, a segunda na 8ª (oitava), a terceira na 13ª (décima
terceira) e posteriormente a cada 5 (cinco) novas vagas que eventualmente forem preenchidas.

8.2.2. A convocação dos candidatos que se declararem indígenas deverá obedecer ao seguinte critério: a primeira
contratação ocorrerá na 10ª (décima) vaga aberta, a segunda na 20ª (vigésima), a terceira na 30ª (trigésima) e
posteriormente a cada 10 (dez) novas que forem eventualmente preenchidas, considerando se tratar de concurso
público para cadastro reserva.

8.6.18. As vagas reservadas aos candidatos que se declararem negros ou indígenas que não forem providas por
falta de candidatos, por reprovação no concurso público ou por não enquadramento no programa de reserva de
vagas serão preenchidas pelos demais candidatos habilitados, com estrita observância à ordem geral de
classificação.

12.4. Na ausência de candidatos aprovados suficientes para composição de cadastro reserva até o limite previsto
nas tabelas do subitem anterior, o quantitativo previsto para candidatos negros, indígenas e/ou pessoa com
deficiência será revertido para a ampla concorrência.


Comentários pessoais:
Não foi falado de pcd, mas vou considerar a seguinte proporção (de acordo com os itens destacados anteriormente):
A cada 10, começando da segunda posição(n vai fazer diferença, só tiveram 7 aprovados...)

Obs.:
1) Nenhum indígena foi aprovado;
2) Apenas 7/44 pcds aprovados.
'''

file_classification = 'database/obj_preliminar.xlsx'
file_positions_index = 'database/positions_index.xlsx'

# leitura dos dados
df_classification = pd.read_excel(file_classification, dtype=str)
df_positions_index = pd.read_excel(file_positions_index)

# criando os dataframes exclusivos para cada modalidade
df_classification_ampla = df_classification[df_classification['MODALIDADE'] == 'Ampla Concorrência']
df_classification_negro = df_classification[df_classification['MODALIDADE'] == 'Pretos ou Pardos']
df_classification_indio = df_classification[df_classification['MODALIDADE'] == 'Indígenas']
df_classification_pcd = df_classification[df_classification['MODALIDADE'] == 'PcD - Pessoa com Deficiência']


def choose_applicant(vancacy_type, df_classification_ampla, df_classification_negro, df_classification_indio,
                     df_classification_pcd):  # essa função retorna a 1a linha do DataFrame filtrado como uma Series
    if vancacy_type == 'Ampla' and not df_classification_ampla.empty:
        return df_classification_ampla.iloc[0]
    elif vancacy_type == 'Negro' and not df_classification_negro.empty:
        return df_classification_negro.iloc[0]
    elif vancacy_type == 'Indio' and not df_classification_indio.empty:
        return df_classification_indio.iloc[0]
    elif vancacy_type == 'PcD' and not df_classification_pcd.empty:
        return df_classification_pcd.iloc[0]
    return None


# DataFrame com as colunas finais necessárias
final_df = pd.DataFrame(columns=df_positions_index.columns.tolist() + df_classification.columns.tolist())

# iterando pelas posições e preenchendo as informações
for i, row in df_positions_index.iterrows():  # n vetorizei mas honestamente, mó sono pai... deixa isso quieto
    candidate = choose_applicant(row['Tipo_Vaga'], df_classification_ampla, df_classification_negro,
                                 df_classification_indio, df_classification_pcd)
    if candidate is None:
        # preenchendo com candidato da ampla concorrência se não houver candidato para a cota especificada e como o núme
        #_ro de inscrições da ampla foi bem maior que o comportado, não vou me preocupar com row['Tipo_Vaga'] = 'Ampla'
        candidate = df_classification_ampla.iloc[0]
        df_classification_ampla = df_classification_ampla[
            df_classification_ampla['INSCRIÇÃO'] != candidate['INSCRIÇÃO']
        ]
    else:
        # removendo o canditado escolhido do dataframe correspondente
        if row['Tipo_Vaga'] == 'Ampla':
            df_classification_ampla = df_classification_ampla[
                df_classification_ampla['INSCRIÇÃO'] != candidate['INSCRIÇÃO']
            ]
        elif row['Tipo_Vaga'] == 'Negro':
            df_classification_negro = df_classification_negro[
                df_classification_negro['INSCRIÇÃO'] != candidate['INSCRIÇÃO']
            ]
        elif row['Tipo_Vaga'] == 'Indio':
            df_classification_indio = df_classification_indio[
                df_classification_indio['INSCRIÇÃO'] != candidate['INSCRIÇÃO']
            ]
        elif row['Tipo_Vaga'] == 'PcD':
            df_classification_pcd = df_classification_pcd[df_classification_pcd['INSCRIÇÃO'] != candidate['INSCRIÇÃO']]

    # salvando a linha no DataFrame final
    final_df = pd.concat([final_df, pd.DataFrame(pd.concat([row, candidate]).to_frame().T)])

# sem tempo e energia para trackear a perda dos 0s à esquerda do nr de inscrição, só vou completar com 0 mesmo...
final_df['INSCRIÇÃO'] = final_df['INSCRIÇÃO'].str.zfill(7)

# só sarvar agora papuxo
final_df.to_excel('database/df/resultado_preliminar_objetivas_ordenado_cota.xlsx', index=False)
