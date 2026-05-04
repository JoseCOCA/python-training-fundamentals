"""Hola mundo del curso python-training-fundamentals.

Es el primer código del curso. Imprime un saludo y la versión de Python con la
que está corriendo, para verificar que el entorno quedó instalado bien.

Cómo ejecutarlo:

    uv run python main.py
"""

import sys

print("Hola desde python-training-fundamentals!")
print(f"Python {sys.version.split()[0]}")
print("Si ves estas tres líneas sin errores, tu entorno está listo.")
