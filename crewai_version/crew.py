from crewai import Agent, Crew, Process, Task
from crewai import Agent, Crew, LLM, Process, Task
from crewai_version.tools.malware_tool import analisar_malware_tool
from crewai_version.tools.ransomware_tool import analisar_ransomware_tool
from crewai_version.tools.phishing_tool import analisar_phishing_tool
from crewai_version.tools.malware_tool import (
    validar_resultado_malware
)
from crewai_version.tools.ransomware_tool import (
    validar_resultado_ransomware
)
from crewai_version.tools.phishing_tool import (
    analisar_phishing_tool,
    validar_resultado_phishing
)

llm_local = LLM(
    model="qwen3.5:9b",
    custom_openai=True,
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)
# ==================================================
# AGENTES
# ==================================================

agente_malware = Agent(
    role="Especialista em Malware",
    goal=(
        "Analisar amostras suspeitas através do modelo "
        "de Machine Learning de Malware disponibilizado."
    ),
    backstory=(
        "És um agente especializado em análise de Malware. "
        "Utilizas exclusivamente a ferramenta de análise "
        "de Malware para obter a classificação produzida "
        "pelo modelo de Machine Learning."
    ),
    tools=[
        analisar_malware_tool
    ],
    llm=llm_local,
    verbose=True,
    allow_delegation=False
)


agente_ransomware = Agent(
    role="Especialista em Ransomware",
    goal=(
        "Analisar amostras suspeitas através do modelo "
        "de Machine Learning de Ransomware disponibilizado."
    ),
    backstory=(
        "És um agente especializado em análise de Ransomware. "
        "Utilizas exclusivamente a ferramenta de análise "
        "de Ransomware para obter a classificação produzida "
        "pelo modelo de Machine Learning."
    ),
    tools=[
        analisar_ransomware_tool
    ],
    llm=llm_local,
    verbose=True,
    allow_delegation=False
)


agente_phishing = Agent(
    role="Especialista em Phishing",
    goal=(
        "Analisar websites através do modelo "
        "de Machine Learning de Phishing disponibilizado."
    ),
    backstory=(
        "És um agente especializado em deteção de Phishing. "
        "Utilizas exclusivamente a ferramenta de análise "
        "de Phishing para obter a classificação produzida "
        "pelo modelo de Machine Learning."
    ),
    tools=[
        analisar_phishing_tool
    ],
    llm=llm_local,
    verbose=True,
    allow_delegation=False
)


# ==================================================
# FUNÇÕES PARA CRIAR TASKS
# ==================================================

def criar_task_malware():

    return Task(
        description=(
            "Existe uma amostra de Malware já preparada "
            "pela aplicação. "

            "Utiliza obrigatoriamente e apenas uma vez "
            "a ferramenta 'Analisar Malware'. "

            "Não classifiques a amostra manualmente. "
            "A decisão deve ser produzida exclusivamente "
            "pelo modelo de Machine Learning. "

            "Não inventes famílias, nomes ou categorias "
            "específicas de malware. "

            "Apresenta exatamente a classificação, "
            "confiança e probabilidades devolvidas "
            "pela ferramenta."
        ),

        expected_output=(
            "Resultado técnico da análise de Malware "
            "com classificação Benigno ou Malware, "
            "confiança e probabilidades. "
            "Não apresentar classificações inventadas."
        ),

        agent=agente_malware,
        guardrail=validar_resultado_malware,
        guardrail_max_retries=2
    )

def criar_task_ransomware():

    return Task(
        description=(
            "Existe uma amostra de Ransomware já preparada "
            "pela aplicação. "

            "Utiliza obrigatoriamente e apenas uma vez "
            "a ferramenta 'Analisar Ransomware'. "

            "Não analises manualmente os dados e "
            "não alteres a classificação produzida "
            "pelo modelo de Machine Learning. "

            "Apresenta exatamente os valores devolvidos "
            "pela ferramenta. "

            "Os valores de 'contribuicao' NÃO representam "
            "percentagens. Não os multipliques por 100 "
            "nem acrescentes o símbolo %. "

            "As probabilidades são valores entre 0 e 1. "
            "Podes apresentar adicionalmente as respetivas "
            "percentagens, mantendo os valores originais. "

            "Não inventes interpretações ou conclusões "
            "não sustentadas pelo resultado técnico."
        ),

        expected_output=(
            "Resultado técnico da análise de Ransomware, "
            "incluindo classificação, confiança, "
            "probabilidades e principais contribuições "
            "das features sem as converter em percentagens."
        ),

        agent=agente_ransomware,
        guardrail=validar_resultado_ransomware,
        guardrail_max_retries=2
    )




def criar_task_phishing():

    return Task(
        description=(
            "Existe uma amostra de Phishing previamente "
            "preparada pela aplicação. "

            "Executa obrigatoriamente a ferramenta "
            "'Analisar Phishing'. "

            "Não analises manualmente a amostra. "
            "Não inventes classificações nem probabilidades. "

            "A classificação deve vir exclusivamente "
            "do modelo de Machine Learning. "

            "Utiliza os valores exatos devolvidos pela Tool. "

            "Os valores de 'contribuicao' não representam "
            "percentagens e não devem ser convertidos. "

            "Não atribuas significados aos valores "
            "-1, 0 ou 1 das features sem documentação."
        ),

        expected_output=(
            "Classificação técnica de Phishing, "
            "confiança, probabilidades e principais "
            "features do modelo XGBoost."
        ),

        agent=agente_phishing,
        guardrail=validar_resultado_phishing,
        guardrail_max_retries=2
    )


# ==================================================
# CRIAR CREW
# ==================================================

def criar_crew(task):
    return Crew(
        agents=[
            task.agent
        ],
        tasks=[
            task
        ],
        process=Process.sequential,
        verbose=True
    )