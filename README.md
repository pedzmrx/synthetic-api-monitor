# Synthetic API Monitor (Serverless)

Projeto de monitoramento sintético de APIs e microsserviços com execução em nuvem baseada em arquitetura Serverless (AWS Lambda, EventBridge, CloudWatch e SNS).

O objetivo é realizar testes automatizados contínuos em rotas críticas, medindo a latência milissegundo a milissegundo e disparando alertas antes que instabilidades afetem os usuários finais.

## Arquitetura da Solução

- **AWS Lambda (Python 3.12):** Executa o cliente de teste sintético sob demanda.
- **Amazon EventBridge:** Dispara a execução automática em intervalos agendados (cron).
- **Amazon CloudWatch:** Armazena logs de execução e métricas de tempo de resposta.
- **Amazon SNS:** Envia alertas imediatos quando são detectadas anomalias ou falhas de SLA.

## Execução Local

O monitor pode ser executado diretamente no terminal local sem dependências externas:

```bash
# Executar a suíte de testes do monitor
python lambda_function.py