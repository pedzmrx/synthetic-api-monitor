import json
import time
import urllib.error
import urllib.request

ENDPOINTS_ALVO = [
    {
        "nome": "API Usuários",
        "url": "https://jsonplaceholder.typicode.com/users",
        "max_latencia_ms": 1500,
    },
    {
        "nome": "API Posts",
        "url": "https://jsonplaceholder.typicode.com/posts/1",
        "max_latencia_ms": 1000,
    },
    # Endpoint intencional para validação de resiliência e alertas
    {
        "nome": "Rota Inexistente (Simulação)",
        "url": "https://jsonplaceholder.typicode.com/rota_inexistente_404",
        "max_latencia_ms": 1000,
    },
]


def testar_endpoint(alvo):
    """Executa requisição HTTP GET e valida status code e latência em relação ao SLA."""
    url = alvo["url"]
    inicio = time.time()

    requisicao = urllib.request.Request(
        url,
        headers={"User-Agent": "SyntheticMonitor/1.0"}
    )

    try:
        # Timeout definido para evitar execuções travadas no runtime da Lambda
        with urllib.request.urlopen(requisicao, timeout=5) as resposta:
            status_code = resposta.getcode()
            latencia_ms = round((time.time() - inicio) * 1000, 2)
            sucesso = (status_code == 200) and (latencia_ms <= alvo["max_latencia_ms"])

            return {
                "nome": alvo["nome"],
                "url": url,
                "status_code": status_code,
                "latencia_ms": latencia_ms,
                "sucesso": sucesso,
                "erro": None,
            }

    except urllib.error.HTTPError as err:
        latencia_ms = round((time.time() - inicio) * 1000, 2)
        return {
            "nome": alvo["nome"],
            "url": url,
            "status_code": err.code,
            "latencia_ms": latencia_ms,
            "sucesso": False,
            "erro": f"HTTP {err.code}: {err.reason}",
        }

    except Exception as err:
        latencia_ms = round((time.time() - inicio) * 1000, 2)
        return {
            "nome": alvo["nome"],
            "url": url,
            "status_code": 0,
            "latencia_ms": latencia_ms,
            "sucesso": False,
            "erro": str(err),
        }


def lambda_handler(event, context):
    """Handler principal de execução do monitor sintético."""
    print("Iniciando ciclo de monitoramento sintético.")

    falhas = []

    for alvo in ENDPOINTS_ALVO:
        diagnostico = testar_endpoint(alvo)
        status_tag = "PASSOU" if diagnostico["sucesso"] else "FALHOU"

        print(
            f"[{status_tag}] {diagnostico['nome']} | "
            f"Status: {diagnostico['status_code']} | "
            f"Latência: {diagnostico['latencia_ms']}ms"
        )

        if not diagnostico["sucesso"]:
            falhas.append(diagnostico)

    print(f"Execução finalizada: {len(ENDPOINTS_ALVO)} verificados, {len(falhas)} anomalias.")

    return {
        "total_testados": len(ENDPOINTS_ALVO),
        "total_falhas": len(falhas),
        "falhas": falhas,
    }


if __name__ == "__main__":
    lambda_handler(event=None, context=None)