import asyncio
from typing import Dict, List
from .ai_service import classify_one
from .prompts import get_validation_set


async def validate_model() -> Dict:
    validation_set = get_validation_set()

    results = []
    correct = 0
    total = len(validation_set)

    for item in validation_set:
        classification = await classify_one(item["email"])

        categoria_predita = classification.get("categoria", "IMPRODUTIVO")
        categoria_esperada = item["categoria_esperada"]
        is_correct = categoria_predita == categoria_esperada

        if is_correct:
            correct += 1

        results.append({
            "email": item["email"][:50] + "...",
            "esperado": categoria_esperada,
            "predito": categoria_predita,
            "confianca": classification.get("confianca", 0),
            "correto": is_correct,
            "razao_modelo": classification.get("razao", "")
        })

    accuracy = (correct / total) * 100 if total > 0 else 0

    tp = sum(1 for r in results if r["esperado"] == "PRODUTIVO" and r["correto"])
    fp = sum(1 for r in results if r["esperado"] == "IMPRODUTIVO" and not r["correto"])
    tn = sum(1 for r in results if r["esperado"] == "IMPRODUTIVO" and r["correto"])
    fn = sum(1 for r in results if r["esperado"] == "PRODUTIVO" and not r["correto"])

    precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
    recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
    f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0

    return {
        "total_exemplos": total,
        "corretos": correct,
        "incorretos": total - correct,
        "acuracia": round(accuracy, 2),
        "precisao": round(precision, 2),
        "recall": round(recall, 2),
        "f1_score": round(f1_score, 2),
        "matriz_confusao": {
            "verdadeiros_positivos": tp,
            "falsos_positivos": fp,
            "verdadeiros_negativos": tn,
            "falsos_negativos": fn
        },
        "resultados_detalhados": results
    }


async def run_validation_report():
    print("=" * 60)
    print("VALIDAÇÃO DO MODELO DE CLASSIFICAÇÃO DE EMAILS")
    print("=" * 60)
    print("\nExecutando testes com conjunto de validação...\n")

    metrics = await validate_model()

    print(f"📊 MÉTRICAS DE PERFORMANCE:")
    print(f"   Total de exemplos testados: {metrics['total_exemplos']}")
    print(f"   Classificações corretas: {metrics['corretos']}")
    print(f"   Classificações incorretas: {metrics['incorretos']}")
    print(f"   Acurácia: {metrics['acuracia']}%")
    print(f"   Precisão: {metrics['precisao']}%")
    print(f"   Recall: {metrics['recall']}%")
    print(f"   F1-Score: {metrics['f1_score']}%")

    print(f"\n📈 MATRIZ DE CONFUSÃO:")
    cm = metrics['matriz_confusao']
    print(f"   Verdadeiros Positivos (TP): {cm['verdadeiros_positivos']}")
    print(f"   Falsos Positivos (FP): {cm['falsos_positivos']}")
    print(f"   Verdadeiros Negativos (TN): {cm['verdadeiros_negativos']}")
    print(f"   Falsos Negativos (FN): {cm['falsos_negativos']}")

    print(f"\n🔍 RESULTADOS DETALHADOS:")
    for i, result in enumerate(metrics['resultados_detalhados'], 1):
        status = "✓" if result['correto'] else "✗"
        print(f"\n   {status} Teste {i}:")
        print(f"      Email: {result['email']}")
        print(f"      Esperado: {result['esperado']}")
        print(f"      Predito: {result['predito']} (confiança: {result['confianca']}%)")
        if not result['correto']:
            print(f"      ⚠️  ERRO - Necessita ajuste no prompt")

    print("\n" + "=" * 60)
    print("ANÁLISE CONCLUÍDA")
    print("=" * 60)

    if metrics['acuracia'] < 80:
        print("\n⚠️  RECOMENDAÇÃO: Acurácia abaixo de 80%")
        print("   - Revisar exemplos de few-shot learning")
        print("   - Adicionar mais casos de borda aos exemplos")
        print("   - Considerar ajuste de temperatura do modelo")
    elif metrics['acuracia'] >= 90:
        print("\n✅ EXCELENTE: Modelo demonstra alta acurácia!")
        print("   - Modelo está bem ajustado para produção")
    else:
        print("\n✓ BOM: Modelo com performance adequada")
        print("   - Considerar refinamento dos prompts para melhorar")

    return metrics

if __name__ == "__main__":
    asyncio.run(run_validation_report())