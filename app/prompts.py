FEW_SHOT_EXAMPLES = """
Exemplos de classificação:

Exemplo 1:
Email: "Prezados, gostaria de solicitar o status da minha solicitação de reembolso enviada no dia 15/03. Aguardo retorno."
Classificação: PRODUTIVO
Confiança: 95
Razão: Solicitação clara que requer ação e resposta específica sobre status de reembolso.

Exemplo 2:
Email: "Oi pessoal! Feliz Ano Novo para todos! Que 2026 seja um ano incrível!"
Classificação: IMPRODUTIVO
Confiança: 98
Razão: Mensagem de felicitação sazonal sem demanda de ação ou resposta.

Exemplo 3:
Email: "Urgente: O sistema está apresentando erro crítico na página de login. Clientes não conseguem acessar. Necessário verificar imediatamente."
Classificação: PRODUTIVO
Confiança: 100
Razão: Problema técnico urgente que demanda ação imediata da equipe.

Exemplo 4:
Email: "Obrigado pela ajuda de ontem! Consegui resolver o problema. Vocês são demais!"
Classificação: IMPRODUTIVO
Confiança: 90
Razão: Agradecimento que não requer resposta ou ação adicional.

Exemplo 5:
Email: "Prezado, preciso atualizar meu endereço de cobrança. Como devo proceder? Anexei os documentos necessários."
Classificação: PRODUTIVO
Confiança: 95
Razão: Solicitação de atualização cadastral que requer processamento e resposta.
"""


def get_classification_prompt(email_content: str) -> str:
    return f"""Você é um assistente especializado em classificar emails corporativos.

{FEW_SHOT_EXAMPLES}

Agora classifique o email abaixo seguindo o mesmo padrão dos exemplos:

Classifique o email em uma das categorias:
- PRODUTIVO: Requer ação, resposta ou acompanhamento (reunião, prazo, rh, orçamento, suporte técnico, atualização de dados, etc)
- IMPRODUTIVO: Não requer ação imediata (saudações, agradecimentos, felicitações, cupons, spam, etc)

Email:
{email_content}

Responda APENAS no formato JSON:
{{
  "categoria": "PRODUTIVO" ou "IMPRODUTIVO",
  "confianca": 0-100,
  "razao": "breve explicação baseada no contexto"
}}
"""


def get_response_prompt(email_content: str, categoria: str) -> str:
    if categoria == "PRODUTIVO":
        contexto = """Para emails PRODUTIVOS:
- Reconheça a solicitação do remetente
- Indique os próximos passos ou prazo de resolução
- Seja específico e objetivo
- Mantenha tom profissional mas acessível
- Ofereça canal adicional de contato se necessário"""
    else:
        contexto = """Para emails IMPRODUTIVOS:
- Responda de forma educada e cordial
- Seja breve e direto
- Reconheça a mensagem sem criar expectativas de ação
- Mantenha tom leve e amigável"""

    return f"""Gere uma resposta automática profissional e cordial para o email classificado como {categoria}.

{contexto}

Email original:
{email_content}

A resposta deve:
- Ter 2-3 parágrafos curtos
- Ser clara e objetiva
- Usar tom profissional mas amigável
- Não incluir assinatura (será adicionada automaticamente)

Gere apenas a resposta, sem explicações adicionais.
"""

VALIDATION_SET = [
    {
        "email": "Preciso urgentemente do relatório financeiro do Q1. Prazo até sexta-feira.",
        "categoria_esperada": "PRODUTIVO",
        "razao": "Solicitação urgente com prazo definido"
    },
    {
        "email": "Parabéns pela promoção! Você merece!",
        "categoria_esperada": "IMPRODUTIVO",
        "razao": "Mensagem de congratulações"
    },
    {
        "email": "O servidor de produção está fora do ar. Clientes reportando erro 503.",
        "categoria_esperada": "PRODUTIVO",
        "razao": "Problema crítico que requer ação imediata"
    },
    {
        "email": "Aproveitando para agradecer o suporte de sempre. Forte abraço!",
        "categoria_esperada": "IMPRODUTIVO",
        "razao": "Agradecimento sem demanda de ação"
    },
    {
        "email": "Gostaria de agendar uma reunião para discutir o novo projeto. Você tem disponibilidade na quinta?",
        "categoria_esperada": "PRODUTIVO",
        "razao": "Solicitação de agendamento"
    },
]

def get_validation_set():
    """Retorna conjunto de validação para teste do modelo"""
    return VALIDATION_SET