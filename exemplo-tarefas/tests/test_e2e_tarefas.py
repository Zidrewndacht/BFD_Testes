from playwright.sync_api import expect

def test_adicionar_tarefa_fluxo_completo(page, servidor):
    # 1. Navega até a URL do nosso servidor Flask
    page.goto(servidor)

    # 2. Localiza o input pelo placeholder e preenche
    page.get_by_placeholder("Descrição da tarefa").fill("Estudar Playwright")

    # 3. Localiza o botão pelo seu texto (role) e clica
    page.get_by_role("button", name="Adicionar").click()

    # 4. Verifica se a tarefa apareceu na lista
    # O Playwright espera automaticamente o JS processar o fetch e atualizar o DOM!
    expect(page.get_by_text("Estudar Playwright")).to_be_visible()

def test_input_eh_limpo_apos_adicionar(page, servidor):
    page.goto(servidor)
    input_tarefa = page.get_by_placeholder("Descrição da tarefa")
    
    input_tarefa.fill("Tarefa temporária")
    page.get_by_role("button", name="Adicionar").click()
    
    # Espera a tarefa aparecer para garantir que o fetch terminou
    expect(page.get_by_text("Tarefa temporária")).to_be_visible()
    
    # Verifica se o input foi limpo pelo JS
    expect(input_tarefa).to_be_empty()

def test_formulario_nao_envia_vazio(page, servidor):
    page.goto(servidor)
    
    # Clica direto sem preencher
    page.get_by_role("button", name="Adicionar").click()
    
    # A tarefa " " (espaço) ou vazia não deve aparecer na lista.
    # O expect com not_to_be_visible ou to_have_count é útil aqui.
    # Vamos verificar que não existe nenhum <li> com texto vazio ou apenas espaços.
    lista = page.locator("#lista-tarefas li")
    expect(lista).to_have_count(0) # O banco de teste começa vazio

def test_adicionar_multiplas_tarefas(page, servidor):
    page.goto(servidor)
    input_tarefa = page.get_by_placeholder("Descrição da tarefa")
    botao = page.get_by_role("button", name="Adicionar")
    
    tarefas = ["Comprar pão", "Estudar Python", "Pagar contas"]
    
    for nome in tarefas:
        input_tarefa.fill(nome)
        botao.click()
        # Espera cada uma aparecer antes de adicionar a próxima
        expect(page.get_by_text(nome)).to_be_visible()
        
    # Verificação final
    expect(page.get_by_text("Comprar pão")).to_be_visible()
    expect(page.get_by_text("Estudar Python")).to_be_visible()
    expect(page.get_by_text("Pagar contas")).to_be_visible()