def get_system_prompt_domains() -> str:
    """
    Retorna um dicionário com system_message e message formatados.
    
    Args:
        dominios: Lista de strings contendo os domínios a analisar
        
    Returns:
        Dicionário contendo system_message e message
    """
    return f"""Avalie cada domínio de 1 a 5 considerando os critérios abaixo e retorne
                        APENAS um array JSON válido, sem texto adicional, sem markdown, sem backticks.

                        CRITÉRIOS:

                        1. TESTE DO RÁDIO
                        O domínio pode ser ditado verbalmente em um programa de rádio e qualquer
                        ouvinte consegue digitar corretamente sem pedir para soletrar? Domínios
                        com letras soltas (lg, dr+iniciais), hífens ou grafia ambígua reprovam.

                        2. FONÉTICA
                        O domínio soa bem e flui naturalmente quando lido em voz alta em português?

                        3. MEMORIZAÇÃO
                        Uma pessoa consegue lembrar o domínio após ouvir uma única vez?

                        4. TAMANHO
                        Até 15 caracteres antes do ponto: ótimo. 16 a 22: aceitável. Acima de 22: ruim.

                        5. AMBIGUIDADE VISUAL
                        Lido junto sem espaços, gera alguma palavra estranha, duplo sentido ou
                        combinação constrangedora?

                        6. GEMINAÇÃO
                        Possui consoantes duplicadas que não fazem parte da grafia correta do
                        português (ex: ll, tt, mm, pp)? Se sim, penalize.

                        7. IDENTIDADE
                        O domínio representa claramente quem é o titular ou o serviço oferecido?

                        8. CATEGORIA
                        O domínio se encaixa claramente em uma categoria de negócio ou setor específico?
                        exemplo: saúde, educação, tecnologia, finanças, jogos, pets, etc. Se sim, qual?

                        FORMATO DE SAÍDA — retorne exatamente esta estrutura para cada domínio:

                        {{
                            "domain": "nome.ext.br",
                            "score": <1 a 5>,
                            "radio_test": <true ou false>,
                            "phonetics": <true ou false>,
                            "memorability": <true ou false>,
                            "size_ok": <true ou false>,
                            "no_ambiguity": <true ou false>,
                            "no_gemination": <true ou false>,
                            "clear_identity": <true ou false>,
                            "category": <categoria ou setor identificado, ou null se não for possível identificar>,
                            "description": "<justificativa curta em português>"
                        }}"""


def get_user_prompt_domain(domain: str, size: int) -> str:
    """
    Retorna a mensagem do usuário para análise de um domínio específico.
    
    Args:
        domain: String contendo o domínio a analisar
        size: Tamanho do domínio
        
    Returns:
        String formatada para o prompt do usuário
    """
    return f"Analise o domínio: {domain} (tamanho até o primeiro ponto: {size})"