<!-- Tradução de README.md, sincronizada em 2026-08-10. O inglês é o canônico:
     ao alterar o README.md, atualize este arquivo na mesma leva. -->

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo/oab-logo-on-dark.png">
  <img src="assets/logo/oab-logo-on-light.png" alt="OAB — Open Architecture Brain" width="420">
</picture>

**Seu agente sabe como são os grandes sistemas. Não sabe o que o seu precisa.**

> Open knowledge. Open reasoning. Open architecture.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Scenarios](https://img.shields.io/badge/scenarios-5%2F5%20passing-brightgreen.svg)](evaluations/)
[![Release](https://img.shields.io/badge/release-v0.1.7%20·%20M1-brightgreen.svg)](https://github.com/mhayk/oab/releases/tag/v0.1.7)

[English](README.md) · **Português (BR)** · [Español](README.es.md)

---

## O problema

Peça a um agente de código para "projetar uma API escalável" e você geralmente recebe Kubernetes,
Kafka, Redis e três microsserviços — para um produto com 100 usuários e um desenvolvedor.

O agente aprendeu a *estética* de system design em palestras e posts de blog, extraídos quase
inteiramente do 0,1% maior dos sistemas. Ele não aprendeu a *economia*.

**100 usuários a 40 requisições por sessão são 0,28 requisições por segundo.** Uma única instância
tem quatro ordens de grandeza de folga. O OAB calcula isso, diz isso, e nomeia a medição exata que
mudaria a resposta.

## O que o OAB faz

| Comando | O que você recebe |
| :-- | :-- |
| `/oab:design` | Uma arquitetura com os números por trás, os componentes recusados e o limiar que mudaria cada resposta |
| `/oab:review` | Achados calibrados pela escala em que seu repositório realmente roda — não um checklist emprestado de um sistema mil vezes maior |
| `/oab:capacity` | Quanto custa uma mudança antes de você fazê-la: requisições/segundo, crescimento de armazenamento, egress, custo, com a fórmula impressa para conferir |
| `/oab:adr` | Uma decisão registrada com as opções que você pesou e a métrica que faria você revisitá-la |

Uma skill de fundo também carrega automaticamente, então a conversa comum sobre arquitetura recebe
a mesma proporcionalidade — não só estes quatro comandos.

## Instalação

```
/plugin marketplace add mhayk/oab
/plugin install oab@oab
```

![Instalando o OAB — real, sem encenação](demo/out/install.gif)

Verificado de ponta a ponta: clone limpo em 0,8 s / 8,1 MB, e os exemplos commitados incluem uma
execução real de `/oab:design` que passa em todas as assertions de cenário e uma revisão real de um
repositório de terceiros com todas as citações de evidência conferidas
([`examples/live-run/`](examples/live-run/), [`examples/live-review/`](examples/live-review/)).
Uma ressalva: os hooks de validação de artefato não dispararam para plugins instalados via
marketplace em sessões headless ([#45](https://github.com/mhayk/oab/issues/45)); a validação no
nível da skill é o fallback até isso ser resolvido.

## Como é a saída

O coração determinístico — mesmas entradas, mesmos números, conferíveis à mão
([`demo/`](demo/) guarda os tapes; nada é encenado):

![O envelope de capacidade: premissas, fórmula, cálculo, sensibilidade](demo/out/calculator.gif)

E de [`examples/tiny-startup/`](examples/tiny-startup/) — 100 usuários, £50/mês, dois
desenvolvedores:

```
## Complexity: 4 / 4  — no headroom

| Component                    | Kind                  | Cost | Why                                    |
| Application instance         | application-runtime   |    1 | 0.28 peak RPS against a single          |
|                              |                       |      | instance leaves ~4 orders of magnitude  |
|                              |                       |      | of headroom.                            |
| Managed relational database  | relational-database   |    1 | 0.66 GB/year. Managed for tested        |
|                              |                       |      | point-in-time recovery, which a         |
|                              |                       |      | two-person team will not build.         |
```

**O que foi rejeitado, e quando revisitar**

> **`cache`** — A 0,24 leituras/segundo no pico, não há pressão de leitura medida para aliviar.
> *Revisitar quando: uma única query exceder 10 requisições/segundo acima de 50 ms, ou a CPU do
> banco ficar sustentada acima de 60% por 3 dias.*

> **`orchestration-platform`** — Três vezes o orçamento de complexidade e quatro vezes o orçamento
> financeiro, para um sistema com quatro ordens de grandeza de folga em uma instância.
> *Revisitar quando: existirem mais de 4 serviços implantáveis de forma independente e houver um
> engenheiro de operações dedicado no time.*

Essa segunda seção — o que foi considerado, recusado, e **a medição que reverte a recusa** — é a
parte que um assistente genérico nunca produz.

## Como ele decide

Cada componente custa **pontos de complexidade**, e cada time tem um orçamento:

```
available = 4 + 1.5 × (engineers − 2) + 4 × dedicated_ops
```

Dois desenvolvedores têm 4 pontos. Um banco gerenciado custa 1; uma plataforma de orquestração
autogerenciada custa 4. Acima do orçamento é **rejeitado por padrão**, e uma exceção precisa nomear
o que será removido ou quem vai operar o excesso.

A cerca de **£240 por ponto por mês** em atenção de engenharia, hospedar o próprio banco para
economizar £250/mês custa aproximadamente £720/mês. O serviço gerenciado é mais barato — e o OAB
diz isso com aritmética, não com preferência.

É uma heurística calibrada, não uma lei — e a saída também diz isso.

## Não é anti-complexidade — é anti-complexidade *injustificada*

Kubernetes, Kafka e Redis são a resposta certa para muitos sistemas. A pergunta é se são a resposta
certa para *este* — e o OAB falha nos próprios testes se errar em qualquer das duas direções.

O cenário 03 em [`evaluations/`](evaluations/) descreve uma plataforma a 50.000 requisições por
segundo em três regiões. As assertions dele **exigem** o maquinário que um sistema pequeno receberia
recusado:

```yaml
must_include_components: [cdn, cache, event-stream, application-runtime]
numeric:
  - { field: "capacity.peak_rps",             min: 40000 }
  - { field: "capacity.egress_gb_per_month",  min: 100000 }   # egress precisa ser calculado
  - { field: "complexity.available",          min: 50 }
```

A suíte falha se o OAB recusar event streaming a 7.500 eventos/segundo com três grupos de
consumidores independentes, ou omitir um CDN diante de 1,04 PB/mês de egress — onde 85% de offload
economiza cerca de $35.000/mês, a maior alavanca de custo daquele desenho.

**Dois dos cinco cenários protegem contra construir de menos; três contra construir demais.** Uma
ferramenta que só evitasse excesso seria uma ferramenta que manda não fazer nada.

## Prova, não promessa

Toda afirmação do OAB é sobre comportamento, e afirmação de comportamento sem teste é marketing.

| | |
| :-- | --: |
| Cenários passando | **5 / 5** |
| — guardas contra construir demais | 3 / 3 |
| — guardas contra construir de menos | 2 / 2 |
| Testes das calculadoras | 43 |
| Fixtures de schema (nos dois sentidos) | 33 |
| Unidades de conhecimento | 37 |

![A suíte de cenários com perturbação de magnitude](demo/out/evaluation.gif)

As assertions rodam contra **campos do artefato**, nunca contra prosa — um framework pode ser
ajustado para produzir palavras tranquilizadoras com muito mais facilidade do que a estrutura
certa. Os cenários também são perturbados em 100× e 0,01× para provar que respondem à magnitude em
vez de reconhecer números específicos.

O cenário 07 é *"nada precisa mudar"*, e o cenário 08 é *"esses requisitos são inconsistentes"*.
São as respostas que um assistente ansioso nunca dá.

## O que ainda não está construído

Lista honesta: sem servidor MCP · sem geração de grafo de conhecimento · sem segunda integração ·
`/oab:evolve` e os outros nove comandos são M2 · nenhum site além de uma landing page · 6 domínios
de conhecimento, não 18.

Veja o [ROADMAP.md](ROADMAP.md) e o [§32 do design](docs/design/07-roadmap-and-risks.md#32-overengineering-review)
— uma crítica ao nosso próprio brief de fundação.

## Contribuindo

**A contribuição de maior valor é conhecimento de arquitetura, e ela não exige entender nada do
código** — copie um template, preencha, abra um pull request.

→ [docs/contributing/knowledge.md](docs/contributing/knowledge.md)

Engine, integrações e avaliação: [CONTRIBUTING.md](CONTRIBUTING.md).

## Apoio

O OAB é gratuito, local-first, e não tem serviço hospedado para monetizar. Se ele conquistar um
lugar no seu fluxo de trabalho, [patrocinar](https://github.com/sponsors/mhayk) financia a parte
sem glamour: manter 37 unidades de conhecimento revisadas e atuais, execuções de avaliação e o
domínio.

## Licença

[Apache-2.0](LICENSE). O nome e o logo do OAB são marcas e não são cobertos por essa licença —
veja o [NOTICE](NOTICE).

[oab.run](https://oab.run/pt/) · [Proposta de design](docs/design/) · [Exemplos](examples/)
