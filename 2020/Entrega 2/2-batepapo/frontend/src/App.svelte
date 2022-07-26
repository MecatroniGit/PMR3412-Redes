<script>

	let chat = [];
	let nome = "";
	let mensagem_enviada = "";

	const ws = new WebSocket("ws://localhost:8765");

	ws.onopen = function() {
		console.log("Cliente se conectou");
	}

	ws.onmessage = function (event) {
		let data = JSON.parse(event.data);
		switch (data["tipo"]) {
			case "confirmacao":
				nome = data["nome"];
				break;
			default:
				chat = [...chat, data];
				break;
		}
	}

	function enviar_mensagem () {
		ws.send(JSON.stringify({mensagem: mensagem_enviada}));
		mensagem_enviada = "";
	}
</script>

<main>
	<h2>Bate-Papo</h2>
	
	<div class="caixa_mensagens">
		{#each chat as item_chat}
		{#if item_chat["tipo"] == "aviso"}
		<div class="container_aviso">
			<div>{item_chat["conteudo"]}</div>
		</div>
		{:else if item_chat["tipo"] == "mensagem" && item_chat["privacidade"] == "privada"}
		<div class="container_mensagem mensagem_privada">
			<div style="color: #fd5634; font-weight: bold;">{item_chat["username"]}</div>
			<div style="margin-left: 5px;">{item_chat["conteudo"]}</div>
		</div>
		{:else}
		<div class="container_mensagem">
			<div style="color: #fd5634; font-weight: bold;">{item_chat["username"]}</div>
			<div style="margin-left: 5px;">{item_chat["conteudo"]}</div>
		</div>
		{/if}
		{/each}
	</div>

	<div style="display: flex; width: 100%;">
		<form style="display: flex; flex-direction: line;">
			<div class="nome">{nome}</div>
			<input type="text" placeholder="Envie sua mensagem" bind:value={mensagem_enviada}/>
			<button type="submit" on:click|preventDefault={enviar_mensagem}>Enviar</button>
		</form>
	</div>

</main>

<style>
	main {
		display: flex;
		flex-direction: column;
		align-items: center;
		width: 480px;
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	.container_mensagem {
		display: flex;
		margin: 5px;
		color: #1d1d1d;
		font-size: 16px;
	}
	.container_aviso {
		display: flex;
		margin: 5px;
		font-weight: thin;
		font-size: 14px;
		color: rgb(126, 126, 126);
	}

	.caixa_mensagens {
		width: 100%;
		height: 11em;
		margin-bottom: 1em;
		background-color: #eaebee;
		overflow: scroll;
		display: flex;
		flex-direction: column;
		align-items: left;
		justify-content: end;
	}

	.mensagem_privada {
		background-color: #cfd0d5;
	}

	.nome {
		margin: 5px;
		color: #fd5634;
		font-weight: bold;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>