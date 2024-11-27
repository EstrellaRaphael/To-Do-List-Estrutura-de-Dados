// aplicar tema salvo no localstorage quando carregar a pagina
document.addEventListener("DOMContentLoaded", () => {
    const botaoAlterarTema = document.getElementById("botaoAlterarTema");

    // verificar no localstorage
    const temaSalvo = localStorage.getItem("theme");
    if (temaSalvo) {
        document.body.setAttribute("data-bs-theme", temaSalvo);
        botaoAlterarTema.textContent = temaSalvo === "dark" ? "Modo Claro" : "Modo Escuro";
    } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        document.body.setAttribute("data-bs-theme", "dark");
        botaoAlterarTema.textContent = "Modo Claro";
    }

    // alterar quando clicar
    botaoAlterarTema.addEventListener("click", () => {
        const temaAtual = document.body.getAttribute("data-bs-theme");
        const novoTema = temaAtual === "light" ? "dark" : "light";
        document.body.setAttribute("data-bs-theme", novoTema);
        botaoAlterarTema.textContent = novoTema === "dark" ? "Modo Claro" : "Modo Escuro";

        // salvar preferencia
        localStorage.setItem("theme", novoTema);
    });
});



// excluir tarefa
const deleteModal = document.getElementById('confirmDeleteModal');
const deleteConfirmButton = document.getElementById('deleteConfirmButton');

deleteModal.addEventListener('show.bs.modal', (event) => {
    const button = event.relatedTarget; // Botão que acionou o modal
    const tarefaId = button.getAttribute('data-id'); // Obtém o ID da tarefa
    if (button.getAttribute('href').includes('pendente')) {
        deleteConfirmButton.setAttribute('href', `/deletar_pendente/${tarefaId}`);
    } else {
        deleteConfirmButton.setAttribute('href', `/deletar_concluida/${tarefaId}`);
    }
});