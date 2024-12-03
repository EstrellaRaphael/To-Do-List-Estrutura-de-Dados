// Evento que é acionado quando o conteúdo da página foi carregado
document.addEventListener("DOMContentLoaded", () => {
    // Obtém o botão para alterar o tema
    const botaoAlterarTema = document.getElementById("botaoAlterarTema");

    // Verifica se há um tema salvo no localStorage
    const temaSalvo = localStorage.getItem("theme");
    if (temaSalvo) {
        // Aplica o tema salvo (escuro ou claro) ao body
        document.body.setAttribute("data-bs-theme", temaSalvo);
        // Atualiza o texto do botão conforme o tema
        botaoAlterarTema.textContent = temaSalvo === "dark" ? "Modo Claro" : "Modo Escuro";
    } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        // Se não houver tema salvo, aplica o tema escuro se o sistema preferir esse modo
        document.body.setAttribute("data-bs-theme", "dark");
        botaoAlterarTema.textContent = "Modo Claro";
    }

    // Adiciona evento de clique para alterar o tema
    botaoAlterarTema.addEventListener("click", () => {
        // Obtém o tema atual aplicado ao body
        const temaAtual = document.body.getAttribute("data-bs-theme");
        // Define o novo tema com base no tema atual
        const novoTema = temaAtual === "light" ? "dark" : "light";
        // Aplica o novo tema ao body
        document.body.setAttribute("data-bs-theme", novoTema);
        // Atualiza o texto do botão conforme o novo tema
        botaoAlterarTema.textContent = novoTema === "dark" ? "Modo Claro" : "Modo Escuro";

        // Salva a preferência de tema no localStorage
        localStorage.setItem("theme", novoTema);
    });
});


// Excluir tarefa - Manipulação do Modal de confirmação de exclusão
const deleteModal = document.getElementById('confirmDeleteModal');
const deleteConfirmButton = document.getElementById('deleteConfirmButton');

// Evento que é acionado quando o modal de confirmação de exclusão é exibido
deleteModal.addEventListener('show.bs.modal', (event) => {
    // Obtém o botão que acionou o modal
    const button = event.relatedTarget;
    // Obtém o ID da tarefa do atributo 'data-id' do botão
    const tarefaId = button.getAttribute('data-id');

    // Verifica se o botão pertence à exclusão de tarefa pendente ou concluída
    if (button.getAttribute('href').includes('pendente')) {
        // Se for tarefa pendente, altera o 'href' do botão de confirmação para deletar a tarefa pendente
        deleteConfirmButton.setAttribute('href', `/deletar_pendente/${tarefaId}`);
    } else {
        // Se for tarefa concluída, altera o 'href' do botão de confirmação para deletar a tarefa concluída
        deleteConfirmButton.setAttribute('href', `/deletar_concluida/${tarefaId}`);
    }
});
