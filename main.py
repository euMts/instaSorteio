from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from time import sleep
import wordlists
import importlib
import constants
import requests
import random
import os

# - DEFININDO VARIAVEIS -
url = constants.urlSorteio
wordlist = wordlists.wordlist1
contas = constants.contas
senhas = constants.senhas
telegram = constants.telegram
telegramApiKey = constants.telegramApiKey
telegramChatId = constants.telegramChatId
esconderNavegador = constants.esconderNavegador
ativas = []
drivers = [] # diferentes nomes para drivers do selenium, diferentes instancias de navegador
rodar = True

# - DEFININDO FUNCÕES -
# ENVIAR MENSAGEM TELEGRAM
def telegramBotSendtext(message):
    send_text = 'https://api.telegram.org/bot' + telegramApiKey + '/sendMessage?chat_id=' + telegramChatId + '&parse_mode=Markdown&text=' + message
    response = requests.get(send_text)
    return response.json()

# ESCONDER CARACTERES DE UMA STRING
def password(entrada):
    temp = ""
    for x in range(len(entrada)):
        temp += "*"
    return temp

# SORTEAR PALAVRA DE UM ARRAY (wordlist)
def palavraRandom(array): # palavraRandom(wordlist))
    palavra = array[random.randint(0, (len(array)-1))]
    return palavra

# GERAR INSTANCIA DOS NAVEGADORES
def gerarInstancias(contas, senhas): # gerarInstancias(listaContendoContas, listaContendoSenhas)
    for x in range(len(contas)): # cria x instancias de navegador referentes ao numero de contas subscritas no arquivo constants.py
        options = Options()
        options.headless = esconderNavegador # True: esconder navegador; False: mostrar navegador
        drivers.append(webdriver.Firefox(options=options))
        drivers[x].maximize_window()
        print(f"Iniciando instancia referente a conta:\n'{contas[f'conta{x}']}' de senha {password(str(senhas[f'conta{x}']))}")
        ativas.append(contas[f'conta{x}'])
        try:
            entrarNoInsta(drivers[x], contas[f"conta{x}"], senhas[f"conta{x}"])
            print(f"Instancia de '{contas[f'conta{x}']}' logada e pronta para uso.")
        except Exception as e:
            print(f"Erro durante a inicializacao de '{contas[f'conta{x}']}'", e)
            if telegram == True:
                telegramBotSendtext(f"Funcao gerarInstancias()\nErro durante a inicializacao de '{contas[f'conta{x}']}'\n{e}")
            break
        print()

# ENTRANDO NO INSTAGRAM
def entrarNoInsta(driver, login, senha): # entra na conta x(login, senha) na instancia x(driver)
    loginInputXpath = ('//input[@name="username"]') # input login
    senhaInputXpath = ('//input[@name="password"]') # input senha
    botaoLoginXpath = ('//*[@id="loginForm"]/div/div[3]/button') # botao 'entrar'
    iconeLogadoXpath = ('//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[5]') # icone da foto (verifica se entrou na conta)
    driver.get("https://www.instagram.com/")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, loginInputXpath))) # espera o elemento ficar disponível
    driver.find_element_by_xpath(loginInputXpath).send_keys(login)
    sleep(1)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, senhaInputXpath)))
    driver.find_element_by_xpath(senhaInputXpath).send_keys(senha)
    sleep(1)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, botaoLoginXpath)))
    driver.find_element_by_xpath(botaoLoginXpath).click()
    sleep(1)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, iconeLogadoXpath)))
    sleep(2)

# COMENTAR UMA PALAVRA
def comentar_uma_palavra(driver, palavra, url): # utiliza a instancia x(driver) para comentar a palavra y(palavra) na url z(url)
    textarea1Xpath = ('//textarea[@class="Ypffh"]') # textarea 'inutilizavel'
    textarea2Xpath = ('//textarea[@class="Ypffh focus-visible"]') # textarea 'utilizavel', pois já foi clicada
    postarComentarioXpath = ("//form[@class='X7cDz']//button[@type='submit']") # botao 'comentar'
    if (driver.current_url != url):
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, textarea1Xpath)))
        sleep(2)                  
    try:
        driver.refresh()
        sleep(2)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, textarea1Xpath)))
        driver.find_element_by_xpath(textarea1Xpath).click()
        sleep(2)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, textarea2Xpath)))
        driver.find_element_by_xpath(textarea2Xpath).send_keys(palavra)
        sleep(3)
        driver.find_element_by_xpath(postarComentarioXpath).click()
        sleep(1)
    except Exception as e:
        print("excepted", e)
        if telegram == True:
            telegramBotSendtext(f'Erro na funcao comentar_uma_palavra()\n{e}')

# PEGAR NOME DO SORTEIO DA URL
def pegarNomeDoSorteio(url):
    try:
        nomeXpath = ("//header[@class='Ppjfr UE9AK  wdOqh']/div[2]/div[1]/div[1]") # nome do usuario postador da foto
        options = Options()
        options.headless = True # navegador escondido
        driverx = webdriver.Firefox(options=options)
        driverx.get(url)
        WebDriverWait(driverx, 15).until(EC.visibility_of_element_located((By.XPATH, nomeXpath)))
        nome = driverx.find_element_by_xpath(nomeXpath).text
        driverx.quit()
        return nome
    except Exception as e:
        print(f"Erro {e}")
        if telegram == True:
            telegramBotSendtext(f'Erro na funcao pegarNomeDoSorteio()\n{e}')

# CHECAR TIMEOUT
def checarTimeout(driver): # deve ser utilizada logo apos comentar uma palavra
    timeout = False
    for x in range(50):
        try:
            driver.find_element_by_xpath("//div[contains(@class, 'ToanC XjicZ')]").click() # botao 'tentar novamente' quando timeout ocorre
            driver.refresh()
            #print("timeout LOOP")
            timeout = True
            break # deve quebrar pois o aviso de timeout some depois de um tempo
        except:
            #print("sem timeout")
            timeout = False
        sleep(0.1)
    return timeout

# ADICIONAR AO LOG
def adicionarValorComentarios(lista, numConta): # Pega o valor atual do item conta(numConta) e adiciona 1. | Ex. adicionarValorComentarios(1) = "conta1":"valor anterior + 1"
    try:
        nomeDaLista = lista.__name__
        valorAtual = lista.numComentarios[f'conta{numConta}']
        arquivo = open(f'{nomeDaLista}.py', 'r')
        conteudo = arquivo.read()
        arquivo.close()
        arquivo2 = open(f'{nomeDaLista}.py', 'w')
        arquivo2.write(conteudo.replace(f"'conta{numConta}':{valorAtual}", f"'conta{numConta}':{valorAtual + 1}"))
        arquivo2.close()
    except Exception as e:
        print(f"Erro em {e}\nPossivelmente a conta de numero '{numConta}' nao existe...")

# REMOVER LOG
def removerValorComentarios(lista, numConta): # Pega o valor atual do item conta(numConta) e remove 1. | Ex. removerValor(1) = "conta1":"valor anterior - 1"
    try:
        nomeDaLista = lista.__name__
        valorAtual = lista.numComentarios[f'conta{numConta}']
        arquivo = open(f'{nomeDaLista}.py', 'r')
        conteudo = arquivo.read()
        arquivo.close()
        arquivo2 = open(f'{nomeDaLista}.py', 'w')
        arquivo2.write(conteudo.replace(f"'conta{numConta}':{valorAtual}", f"'conta{numConta}':{valorAtual - 1}"))
        arquivo2.close()
    except Exception as e:
        print(f"Erro em {e}\nPossivelmente a conta de numero '{numConta}' nao existe...")

# DEFINIR TOTAL DE COMENTARIOS
def totalComentarios():
    soma = 0
    for x in range(len(constants.numComentarios)):
        soma += constants.numComentarios[f"conta{x}"]
    return soma

# DEFINIR TODAS CONTAS COMO ATIVAS
def todasContasAtivas():
    ativas.clear()
    for x in range(len(contas)):
        ativas.append(contas[f"conta{x}"])
    return ativas

# ENCERRAR TODOS OS DRIVERS
def encerrarDrivers():
    for x in range(len(drivers)):
        drivers[x].quit()

# ADICIONAR 1 A VARIÁVEL CICLOS NA LISTA
def adicionarValorCiclos(lista):
    try:
        nomeDaLista = lista.__name__
        valorAtual = lista.ciclos
        arquivo = open(f'{nomeDaLista}.py', 'r')
        conteudo = arquivo.read()
        arquivo.close()
        arquivo2 = open(f'{nomeDaLista}.py', 'w')
        arquivo2.write(conteudo.replace(f"ciclos = {valorAtual}", f"ciclos = {valorAtual + 1}"))
        arquivo2.close()
        importlib.reload(constants)
    except Exception as e:
        print(f"Erro em {e}\nCiclos falhos...")

# ZERAR A VARIÁVEL CICLOS NA LISTA
def zerarCiclos(lista):
    try:
        nomeDaLista = lista.__name__
        valorAtual = lista.ciclos
        arquivo = open(f'{nomeDaLista}.py', 'r')
        conteudo = arquivo.read()
        arquivo.close()
        arquivo2 = open(f'{nomeDaLista}.py', 'w')
        arquivo2.write(conteudo.replace(f"ciclos = {valorAtual}", f"ciclos = 0"))
        arquivo2.close()
        importlib.reload(lista)
    except Exception as e:
        print(f"Erro em {e}\nCiclos falhos...")

# ARMAZENAR CONTAS EM QUARENTENA
def adicionarQuarentena(lista, conta):
    try:
        nomeDaLista = lista.__name__
        quarentenaAtual = lista.quarentena
        if conta not in quarentenaAtual:
            conta = (f"'{conta}'")
            arquivo = open(f'{nomeDaLista}.py', 'r')
            conteudo = arquivo.read()
            arquivo.close()
            arquivo2 = open(f'{nomeDaLista}.py', 'w')
            quarentenaString = str(quarentenaAtual).replace("]", "")
            if (len(quarentenaAtual) == 0):
                arquivo2.write(conteudo.replace(f"quarentena = {quarentenaAtual}", f"quarentena = {f'{quarentenaString}{conta}]'}"))
            else:
                arquivo2.write(conteudo.replace(f"quarentena = {quarentenaAtual}", f"quarentena = {f'{quarentenaString}, {conta}]'}"))
            arquivo2.close()
        importlib.reload(lista)
    except Exception as e:
        print(f"Erro em {e}\Quarentena falha...")

# LIMPAR QUARENTENA
def limparQuarentena(lista):
    try:
        nomeDaLista = lista.__name__
        quarentenaAtual = lista.quarentena
        arquivo = open(f'{nomeDaLista}.py', 'r')
        conteudo = arquivo.read()
        arquivo.close()
        arquivo2 = open(f'{nomeDaLista}.py', 'w')
        quarentenaString = str(quarentenaAtual).replace("]", "")
        arquivo2.write(conteudo.replace(f"quarentena = {quarentenaAtual}", f"quarentena = []"))
        arquivo2.close()
        importlib.reload(lista)
    except Exception as e:
        print(f"Erro em {e}\Quarentena falha...")

# LIMPAR QUARENTENA A CADA 11 CICLOS
# obs. um ciclo é uma vez que o loop roda.
# levando em conta a randomização do maior número possível, cada ciclo tem em média 170 minutos (10200 segundos).
# utilizaremos 30 horas de delay
# 30 horas = 1800 minutos = 108000 segundos
# 108000/10200 = 10,5 (arredondaremos para 11) ciclos.
def verificarQuarentena():
    if (constants.ciclos == 11):
        zerarCiclos(constants)
        limparQuarentena(constants)
        todasContasAtivas()
        print("Quarentena zerada.")
    else: 
        adicionarValorCiclos(constants)

# - INICIALIZACAO -
gerarInstancias(contas, senhas)
nomeDoSorteio = pegarNomeDoSorteio(url)

# - LOOP -
while rodar == True:
    try:
        for x in range(10): # rodar a funcao x vezes
            for y in range(len(contas)): # rodar em todas as contas (y)
                if (contas[f"conta{y}"] in constants.quarentena):
                    pass # pula para o próximo valor de y
                else:
                    comentar_uma_palavra(drivers[y], palavraRandom(wordlist), url)
                    if checarTimeout(drivers[y]) == True:
                        #quarentena.append(contas[f"conta{y}"])
                        adicionarQuarentena(constants, contas[f"conta{y}"])
                        for z in range(len(ativas)):
                            if ativas[z] == contas[f"conta{y}"]:
                                ativas.pop(z)
                                break
                    else:
                        adicionarValorComentarios(constants, y)
                    importlib.reload(constants)        
                    os.system("cls")
                    print(f"Participando do sorteio de: {nomeDoSorteio}\nContas ativas no momento: [{len(ativas)}] {ativas}\nTotal de comentários: {totalComentarios()}\nQuarentena: {constants.quarentena}")
            sleep(random.randint(300, 480)) # 300s = 5min  480s = 8min (waves de 10 comentários em todas as contas com delay entre 5 e 8 min)
        sleep(random.randint(2400, 5400)) # 2400s = 40min | 5400s = 90min (depois de completar 10 waves gerar delay entre 40 e 90 minutos)
        verificarQuarentena()
    except Exception as e:
        print(e)
        if telegram == True:
            telegramBotSendtext(f"Erro geral em\n'{e}'\nFinalizando.")
        encerrarDrivers()
        rodar = False