from schemas import Domain, DomainDetail


def separate_domains_with_numbers(domains: list[Domain]):
    """
    Separa domínios que contêm números dos que não contêm.
    
    Args:
        domains (list): Lista de domínios
        
    Returns:
        tuple: (domínios_com_números, domínios_sem_números)
    """
    domains_with_numbers = []
    domains_without_numbers = []
    
    for d in domains:
        if any(char.isdigit() for char in d.domain):
            domains_with_numbers.append(d)
        else:
            domains_without_numbers.append(d)
    
    return domains_with_numbers, domains_without_numbers


def separate_domains_by_extension(domains: list[Domain], preferred_extensions: list[str]):
    """
    Separa domínios que contêm pontos além das extensões preferenciais.
    
    Args:
        domains (list): Lista de domínios
        preferred_extensions (list): Lista de extensões preferenciais (ex: ['.com.br', '.adv.br'])
        
    Returns:
        tuple: (domínios_com_pontos_extras, domínios_com_extensoes_preferidas)
    """
    domains_with_extra_dots = []
    domains_with_preferred_extensions = []
    
    for d in domains:
        if any(d.domain.endswith(ext) for ext in preferred_extensions):
            domains_with_preferred_extensions.append(d)
        else:
            domains_with_extra_dots.append(d)
    
    return domains_with_extra_dots, domains_with_preferred_extensions


def separate_domains_by_special_chars(domains: list[Domain], preferred_extensions: list[str]):
    """
    Separa domínios que contêm pontos (.) ou hifens (-) além das extensões preferenciais.
    
    Args:
        domains (list): Lista de domínios
        preferred_extensions (list): Lista de extensões preferenciais (ex: ['.com.br', '.adv.br'])
        
    Returns:
        tuple: (domínios_com_pontos_ou_hifens, domínios_limpos)
    """
    domains_with_special_chars = []
    domains_clean = []
    
    for d in domains:
        # Remove a extensão preferencial para verificar se há pontos ou hifens extras
        domain_without_ext = d.domain
        for ext in preferred_extensions:
            if d.domain.endswith(ext):
                domain_without_ext = d.domain[:-len(ext)]
                break
        
        # Verifica se há pontos ou hifens no domínio sem a extensão
        if '.' in domain_without_ext or '-' in domain_without_ext:
            domains_with_special_chars.append(d)
        else:
            domains_clean.append(d)
    
    return domains_with_special_chars, domains_clean


def filter_long_domains(domains: list[Domain], preferred_extensions, char_limit):
    """
    Filtra domínios longos recebendo um limite de corte para separar os maiores.
    
    Args:
        domains (list): Lista de domínios
        preferred_extensions (list): Lista de extensões preferenciais (ex: ['.com.br', '.adv.br'])
        char_limit (int): Limite de caracteres para considerar um domínio como longo
        
    Returns:
        tuple: (domínios_longos_com_tamanho, domínios_curtos_com_tamanho)
            Cada elemento é uma lista de tuplas (domínio, tamanho_sem_extensão)
    """
    long_domains = []
    short_domains = []
    
    for d in domains:
        # Remove a extensão preferencial para contar caracteres
        domain_without_ext = d.domain
        for ext in preferred_extensions:
            if d.domain.endswith(ext):
                domain_without_ext = d.domain[:-len(ext)]
                break
        
        # Conta caracteres sem a extensão
        char_count = len(domain_without_ext)
        
        if char_count > char_limit:
            long_domains.append(Domain(domain=d.domain, detail=DomainDetail(domain=d.domain, extension=ext, length=char_count)))
        else:
            short_domains.append(Domain(domain=d.domain, detail=DomainDetail(domain=d.domain, extension=ext, length=char_count)))
    
    return long_domains, short_domains





