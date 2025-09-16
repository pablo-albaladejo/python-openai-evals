# Python OpenAI Evals - Evaluador de Prompts

Un framework para evaluar y comparar diferentes versiones de prompts usando OpenAI API, inspirado en el proyecto [OpenAI Evals](https://github.com/openai/evals).

## Características

- ✅ **Comparación de múltiples prompts**: Evalúa diferentes versiones de prompts lado a lado
- ✅ **Métricas configurables**: Usa evaluadores básicos como exactitud, similitud, contenido, etc.
- ✅ **Datasets flexibles**: Soporte para JSON y CSV
- ✅ **Reportes completos**: Genera reportes en JSON, CSV y HTML
- ✅ **Configuración YAML**: Configuración fácil a través de archivos YAML
- ✅ **CLI simple**: Interfaz de línea de comandos intuitiva

## Instalación

1. Clona el repositorio:
```bash
git clone <tu-repositorio>
cd python-openai-evals
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura tu API key de OpenAI:
```bash
cp .env.example .env
# Edita .env y añade tu OPENAI_API_KEY
```

## Uso Básico

### 1. Crear un archivo de configuración

```yaml
name: "Mi Evaluación de Prompts"
description: "Comparando diferentes versiones de prompts"

prompt_versions:
  - name: "version_1"
    template: "Traduce: {{ input }}"
    variables: ["input"]

  - name: "version_2"
    template: "Traduce profesionalmente del inglés al español: {{ input }}"
    variables: ["input"]

dataset_path: "mi_dataset.json"
evaluators: ["similarity", "contains"]
openai_model: "gpt-3.5-turbo"
```

### 2. Crear un dataset

```json
{
  "name": "Dataset de Prueba",
  "data": [
    {
      "input": "Hello world",
      "expected": "Hola mundo"
    },
    {
      "input": "How are you?",
      "expected": "¿Cómo estás?"
    }
  ]
}
```

### 3. Ejecutar la evaluación

```bash
python main.py -c mi_config.yaml -o resultados
```

## Ejemplo Completo

Puedes probar el sistema inmediatamente con el ejemplo incluido:

```bash
# Asegúrate de tener tu OPENAI_API_KEY en el archivo .env
python main.py -c prompt_evaluator/examples/example_config.yaml
```

Este ejemplo evalúa 3 diferentes enfoques para traducir texto del inglés al español.

## Estructura del Proyecto

```
python-openai-evals/
├── prompt_evaluator/
│   ├── core/                 # Clases base y lógica principal
│   │   ├── base.py          # Definiciones base (EvaluationResult, BaseEvaluator, etc.)
│   │   ├── config.py        # Carga y manejo de configuración YAML
│   │   ├── dataset.py       # Carga y validación de datasets
│   │   └── evaluator.py     # Motor de evaluación principal
│   ├── evaluators/          # Evaluadores específicos
│   │   └── basic.py         # Evaluadores básicos (exact_match, similarity, etc.)
│   ├── metrics/             # Métricas de análisis
│   │   └── basic.py         # Métricas básicas (average, distribution, etc.)
│   ├── reports/             # Generación de reportes
│   │   └── generator.py     # Generador de reportes en múltiples formatos
│   └── examples/            # Ejemplos de configuración y datasets
├── main.py                  # CLI principal
├── requirements.txt         # Dependencias
└── README.md               # Este archivo
```

## Evaluadores Disponibles

- **exact_match**: Coincidencia exacta con la respuesta esperada
- **contains**: Verifica si la respuesta esperada está contenida en la salida
- **similarity**: Usa SequenceMatcher para calcular similitud textual
- **regex**: Evalúa si la salida coincide con un patrón regex
- **length**: Verifica si la longitud de la salida está en un rango específico
- **json_validity**: Verifica si la salida es JSON válido

## Métricas Disponibles

- **average_score**: Puntuación promedio
- **score_distribution**: Estadísticas de distribución (media, std, percentiles)
- **success_rate**: Porcentaje de resultados por encima de un umbral
- **consistency**: Medida de consistencia en el rendimiento
- **comparison**: Comparación relativa entre versiones de prompts

## Formatos de Salida

Los reportes se generan en múltiples formatos:

- **Consola**: Vista rápida con tablas formateadas
- **JSON**: Datos completos para análisis programático
- **CSV**: Para análisis en hojas de cálculo
- **HTML**: Reporte web navegable

## Personalización

### Crear Evaluadores Personalizados

```python
from prompt_evaluator.core.base import BaseEvaluator

class MiEvaluadorPersonalizado(BaseEvaluator):
    def __init__(self):
        super().__init__("mi_evaluador", "Descripción de mi evaluador")

    def evaluate(self, prompt_output: str, expected_output: str, **kwargs) -> float:
        # Tu lógica aquí
        return score
```

### Crear Métricas Personalizadas

```python
from prompt_evaluator.core.base import BaseMetric

class MiMetricaPersonalizada(BaseMetric):
    def calculate(self, results: List[EvaluationResult]) -> Dict[str, float]:
        # Tu lógica aquí
        return {"mi_metrica": valor}
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/mi-feature`)
3. Commit tus cambios (`git commit -am 'Añade mi feature'`)
4. Push a la rama (`git push origin feature/mi-feature`)
5. Crea un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.