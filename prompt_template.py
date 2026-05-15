def get_prompt_domains(domains: list[str]) -> dict:
    """
    Retorna um dicionário com system_message e message formatados.
    
    Args:
        dominios: Lista de strings contendo os domínios a analisar
        
    Returns:
        Dicionário contendo system_message e message
    """
    domains_str = "\n".join(domains)
    
    system_message = f"""Você é um especialista em análise de domínios para registro de marca no Brasil.
              Analise cada domínio e retorne APENAS um array JSON válido, sem texto adicional, sem markdown, sem backticks
              com a seguinte estrutura para cada um:

                {{
                  "domain": "nomedominio.adv.br",
                  "score": 0-10,
                  "memory": true/false,
                  "radio_test": true/false,
                  "characters": number,
                  "ambiguity": true/false,
                  "recommendation": "register" | "evaluate" | "ignore",
                  "reason": "short explanation"
                }}

                Criteria for score:
                - Up to 15 characters: +2pts
                - 16-22 characters: +1pt
                - Passes the radio test: +2pts
                - No visual or reading ambiguity: +1pt
                - Consistent with professional identity: +1pt
                - Recognizable proper name: +1pt

                Score 8-10 → register
                Score 5-7  → evaluate
                Below 5 → ignore

                Return only the JSON, without explanations or additional text."""
    
    result = {
        "system_message": system_message,
        "message": domains_str
    }
    
    return result
