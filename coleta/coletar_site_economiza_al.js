// Coleta usada em 23/11/2026 no site público do Economiza Alagoas (economizaalagoas.sefaz.al.gov.br).
// Rodada no console da página inicial do site, uma busca por vez, com pausas de 1,5 a 2 s.
// Só a categoria 50000000 (Alimentos / Bebidas / Tabaco). Buscas feitas: FERMENTO, LEITE CONDENSADO,
// CREME DE LEITE, BISCOITO RECHEADO, AGUA MINERAL, ATUM, TODDY, NESCAU.
// Uso em pequena escala; os termos de uso foram pedidos à Sefaz-AL e ainda não foram confirmados.
async function coletar(termo) {
  const b = new URLSearchParams({ textoConsulta: termo });
  const h1 = await (await fetch('/exibicaoPrecoProduto.htm', { method: 'POST', body: b, credentials: 'include' })).text();
  const cats = [...h1.matchAll(/consultarPorCategoria\((\d+)\)/g)].map(m => m[1]);
  if (!cats.includes('50000000')) return { termo, cats, n: 0, rows: [] };
  await new Promise(r => setTimeout(r, 1500));
  const h2 = await (await fetch('/exibicaoPrecoProduto.htm?codSegmentoGPC=50000000', { credentials: 'include' })).text();
  const doc = new DOMParser().parseFromString(h2, 'text/html');
  const rows = [...doc.querySelectorAll('.cartao')].map(c => {
    const t = c.querySelector('.cartao_titulo_texto');
    const v = c.querySelector('.valor_ultima_venda');
    const loja = c.querySelector('.cartao_contribuinte_bloco_esquerdo');
    const oc = [...c.querySelectorAll('[onclick]')].map(e => e.getAttribute('onclick')).join(' ');
    const lj = loja ? loja.innerText.split('\n').map(s => s.trim()).filter(Boolean) : [];
    return {
      termo, desc: t ? t.textContent.trim() : '',
      cb: (oc.match(/consultarPorCodigoBarra\('([^']*)'\)/) || [])[1] || '',
      cac: (oc.match(/exibirEstabelecimento\('([^']*)'\)/) || [])[1] || '',
      loja: lj[0] || '', end: lj.slice(1).join(' | '), preco: v ? v.textContent.trim() : ''
    };
  });
  return { termo, cats, n: rows.length, rows };
}

// Nome da rede: duas primeiras palavras do nome da loja, sem sufixos societários.
function rede(l) {
  l = l.toUpperCase().replace(/[^A-Z0-9 ]/g, ' ')
       .replace(/\b(LTDA|S A|SA|EIRELI|ME|EPP|COMERCIO|DE|DO|DA|E)\b/g, ' ').replace(/\s+/g, ' ').trim();
  return l.split(' ').slice(0, 2).join(' ');
}

// Exportação: uma linha por (descrição, código, rede, termo) com o número de ocorrências.
function exportar(dados) {
  const s = new Map();
  for (const x of dados) { const k = [x.desc, x.cb, rede(x.loja), '', x.termo].join('\t'); s.set(k, (s.get(k) || 0) + 1); }
  return [...s.entries()].map(([k, n]) => { const p = k.split('\t'); return [p[0], p[1], p[2], n, p[4]].join('\t'); });
}
