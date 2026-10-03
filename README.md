# Synthetic API Monitor (Serverless AWS)

Solução de monitoramento sintético contínuo e automação de testes de confiabilidade (QA/SRE) para validação de disponibilidade e latência de APIs REST. O sistema opera em arquitetura 100% orientada a eventos e Serverless na AWS, garantindo custo operacional zero dentro da camada gratuita (AWS Free Tier) e dispensando servidores dedicados.

---

## 1. Visão Geral da Arquitetura

O monitor simula requisições de clientes reais em intervalos regulares. Em caso de violação de SLA de latência ou retorno de códigos de erro HTTP, notificações de incidentes são despachadas imediatamente para os responsáveis técnicos.

Fluxo operacional:
1. O **Amazon EventBridge** dispara a execução a cada 5 minutos.
2. A **AWS Lambda** (Python 3.12) efetua requisições HTTP GET nas APIs e cronometra o tempo de resposta (RTT).
3. O **Amazon CloudWatch Logs** retém toda a telemetria, tempo de execução e memória consumida.
4. Em caso de anomalia, o **Amazon SNS** publica uma mensagem no tópico e entrega o alerta no e-mail cadastrado.

---

## 2. Componentes e Decisões Técnicas

- **Computação (AWS Lambda):** Execução sob demanda (FaaS). Elimina custos ociosos de instâncias EC2 ligadas continuamente para rotinas que executam em milissegundos.
- **Runtime (Python 3.12):** Utilização estrita de módulos nativos da biblioteca padrão (urllib.request, time, json). Reduz o tempo de inicialização a frio (cold start) e dispensa o empacotamento de Lambda Layers.
- **Orquestração (Amazon EventBridge):** Gatilho temporal gerenciado que elimina a necessidade de processos cron em servidores Linux.
- **Mensageria (Amazon SNS):** Arquitetura Pub/Sub que desacopla o robô de teste do canal final de notificação.
- **Segurança (AWS IAM):** Princípio do Menor Privilégio. A Lambda assume uma IAM Role com credenciais temporárias em tempo de execução, sem credenciais fixas no código.
- **Observabilidade (Amazon CloudWatch):** Coleta automática de logs, métricas de duração de execução e uso real de memória.

---

## 3. Critérios de Avaliação e SLAs

Cada ciclo de teste valida:
- **Código de Status HTTP:** O endpoint deve retornar estritamente status 200 OK. Respostas 4xx ou 5xx são tratadas como falha.
- **SLA de Latência:** Tempo de resposta medido em milissegundos comparado com a tolerância máxima definida por rota.
- **Resiliência e Timeout:** Erros de rede, falhas de DNS ou bloqueios superiores a 5 segundos são capturados via exceções sem quebrar a execução.

---

## 4. Estrutura do Repositório

- `lambda_function.py`: Handler de execução, cliente HTTP e integração com AWS SDK (boto3).
- `.gitignore`: Regras de exclusão de artefatos temporários, caches e variáveis locais.
- `README.md`: Documentação técnica e especificações da arquitetura.

---

## 5. Execução Local

O script pode ser validado no ambiente de desenvolvimento local antes do deploy:

```bash
pip install boto3
python lambda_function.py
```

---

## 6. Procedimento de Implantação na AWS

1. **Amazon SNS:** Criar tópico Standard chamado `alerta-falhas-api`, criar assinatura do tipo E-mail, confirmar no link da caixa de entrada e copiar o ARN.
2. **AWS IAM:** Anexar a permissão `AmazonSNSFullAccess` (ou política com ação `sns:Publish`) à Role de execução da Lambda.
3. **AWS Lambda:** Criar função Python 3.12 (x86_64), configurar a variável de ambiente `SNS_TOPIC_ARN` com o ARN do tópico e fazer o Deploy do código.
4. **Amazon EventBridge:** Adicionar gatilho na Lambda com regra agendada: `rate(5 minutes)`.

---

## 7. Análise de Custos (AWS Free Tier)

- **AWS Lambda:** 8.640 execuções mensais (franquia gratuita de 1.000.000 de execuções/mês, consumo < 1%).
- **Amazon EventBridge:** Regras agendadas sem custo adicional.
- **Amazon CloudWatch:** Volume gerado inferior a 50 MB/mês (franquia de até 5 GB de ingestão gratuita).
- **Amazon SNS:** 1.000 notificações de e-mail gratuitas por mês.