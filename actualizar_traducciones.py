#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar traducciones al inglés automáticamente
"""

import re

# Traducciones específicas para los ejemplos
traducciones = {
    # Títulos de ejemplos
    "Problema de Producción Industrial": "Industrial Production Problem",
    "Problema de Planificación Nutricional": "Nutritional Planning Problem", 
    "Problema de Optimización Logística": "Logistics Optimization Problem",
    
    # Descripciones de problemas
    "Una fábrica de muebles produce dos tipos de productos: mesas (Producto A) y sillas (Producto B). La empresa cuenta con recursos limitados de madera y tiempo de producción. Cada mesa genera una ganancia de $3 y cada silla $2. La empresa necesita determinar cuántas unidades de cada producto fabricar para maximizar sus ganancias, considerando que tiene disponibles 18 unidades de madera y 12 horas de tiempo de producción diarias.": 
    "A furniture factory produces two types of products: tables (Product A) and chairs (Product B). The company has limited wood and production time resources. Each table generates a profit of $3 and each chair $2. The company needs to determine how many units of each product to manufacture to maximize its profits, considering that it has 18 units of wood and 12 hours of production time available daily.",
    
    "Un nutricionista necesita diseñar una dieta económica que cumpla con los requerimientos mínimos de nutrientes para un hospital. Dispone de dos tipos de alimentos: Alimento 1 (cuesta $4 por unidad) y Alimento 2 (cuesta $3 por unidad). La dieta debe garantizar al menos 10 unidades de proteína, 8 unidades de vitaminas y 12 unidades de minerales. El objetivo es minimizar el costo total de la dieta mientras se satisfacen todos los requerimientos nutricionales.":
    "A nutritionist needs to design an economical diet that meets the minimum nutrient requirements for a hospital. They have two types of food available: Food 1 (costs $4 per unit) and Food 2 (costs $3 per unit). The diet must guarantee at least 10 units of protein, 8 units of vitamins and 12 units of minerals. The objective is to minimize the total cost of the diet while satisfying all nutritional requirements.",
    
    "Una empresa distribuidora debe transportar productos desde dos almacenes hacia dos tiendas para minimizar los costos de transporte. Cuenta con tres rutas posibles: Ruta 1 (costo $8 por unidad), Ruta 2 (costo $6 por unidad) y Ruta 3 (costo $10 por unidad). El almacén 1 puede enviar máximo 15 unidades por las rutas 1 y 2, el almacén 2 puede enviar máximo 25 unidades por la ruta 3. La tienda 1 necesita al menos 5 unidades y la tienda 2 necesita al menos 15 unidades. ¿Cómo distribuir el transporte para minimizar costos?":
    "A distribution company must transport products from two warehouses to two stores to minimize transportation costs. It has three possible routes: Route 1 (cost $8 per unit), Route 2 (cost $6 per unit) and Route 3 (cost $10 per unit). Warehouse 1 can send a maximum of 15 units via routes 1 and 2, warehouse 2 can send a maximum of 25 units via route 3. Store 1 needs at least 5 units and store 2 needs at least 15 units. How to distribute transportation to minimize costs?",
    
    # Variables
    "x1 (Mesas producidas)": "x1 (Tables produced)",
    "x2 (Sillas producidas)": "x2 (Chairs produced)",
    "x1 (Unidades de Alimento 1)": "x1 (Units of Food 1)",
    "x2 (Unidades de Alimento 2)": "x2 (Units of Food 2)", 
    "x1 (Unidades por Ruta 1)": "x1 (Units via Route 1)",
    "x2 (Unidades por Ruta 2)": "x2 (Units via Route 2)",
    "x3 (Unidades por Ruta 3)": "x3 (Units via Route 3)",
    
    # Tipos de problema
    "Minimización": "Minimization",
    
    # Restricciones
    "2x1 + x2 ≤ 18 (Limitación de madera: cada mesa usa 2 unidades, cada silla 1)": 
    "2x1 + x2 ≤ 18 (Wood limitation: each table uses 2 units, each chair 1)",
    "x1 + 3x2 ≤ 12 (Limitación de tiempo: cada mesa toma 1 hora, cada silla 3 horas)":
    "x1 + 3x2 ≤ 12 (Time limitation: each table takes 1 hour, each chair 3 hours)",
    "2x1 + x2 ≥ 10 (Requerimiento mínimo de proteína)":
    "2x1 + x2 ≥ 10 (Minimum protein requirement)",
    "x1 + x2 ≥ 8 (Requerimiento mínimo de vitaminas)":
    "x1 + x2 ≥ 8 (Minimum vitamin requirement)",
    "x1 + 3x2 ≥ 12 (Requerimiento mínimo de minerales)":
    "x1 + 3x2 ≥ 12 (Minimum mineral requirement)",
    "x1 + x2 ≤ 15 (Capacidad máxima del almacén 1)":
    "x1 + x2 ≤ 15 (Maximum capacity of warehouse 1)",
    "x3 ≤ 25 (Capacidad máxima del almacén 2)":
    "x3 ≤ 25 (Maximum capacity of warehouse 2)",
    "x1 + x3 ≥ 5 (Demanda mínima de la tienda 1)":
    "x1 + x3 ≥ 5 (Minimum demand of store 1)",
    "x2 + x3 ≥ 15 (Demanda mínima de la tienda 2)":
    "x2 + x3 ≥ 15 (Minimum demand of store 2)",
    
    # Categorías
    "Producción": "Production",
    "Dieta": "Diet", 
    "Transporte": "Transportation",
    
    # UI de ejemplos
    "Ejemplos de Programación Lineal": "Linear Programming Examples",
    "Explora problemas reales resueltos paso a paso. Cada ejemplo incluye su formulación matemática completa y puedes cargar los datos directamente en la calculadora para experimentar.":
    "Explore real problems solved step by step. Each example includes its complete mathematical formulation and you can load the data directly into the calculator to experiment.",
    "Problemas Reales": "Real Problems", 
    "Calculadora Integrada": "Integrated Calculator",
    "Paso a Paso": "Step by Step",
    "Todos": "All",
    "Variables": "Variables",
    "Objetivo": "Objective",
    "Restricciones": "Constraints", 
    "Solución Óptima": "Optimal Solution",
    "Calcular Ejemplo": "Calculate Example",
    "¡Practica con tus propios problemas!": "Practice with your own problems!",
    "Ahora que has explorado los ejemplos, es momento de crear y resolver tus propios problemas de programación lineal usando nuestra calculadora interactiva.":
    "Now that you've explored the examples, it's time to create and solve your own linear programming problems using our interactive calculator.",
    "Calculadora Intuitiva": "Intuitive Calculator",
    "Interfaz fácil de usar para crear tus problemas": "User-friendly interface to create your problems",
    "Soluciones Detalladas": "Detailed Solutions",
    "Resultados paso a paso con explicaciones": "Step-by-step results with explanations",
    "Historial Completo": "Complete History",
    "Guarda y revisa tus problemas anteriores": "Save and review your previous problems",
    "Crear Nuevo Problema": "Create New Problem",
    "Ver Ayuda": "View Help"
}

def actualizar_traducciones():
    """Actualiza el archivo messages.po con las traducciones"""
    
    # Leer el archivo
    with open('app/translations/en/LC_MESSAGES/messages.po', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Para cada traducción
    for es, en in traducciones.items():
        # Buscar el patrón msgid "texto" msgstr ""
        patron = f'msgid "{re.escape(es)}"\nmsgstr ""'
        reemplazo = f'msgid "{es}"\nmsgstr "{en}"'
        
        # Reemplazar si se encuentra
        if patron in contenido:
            contenido = contenido.replace(patron, reemplazo)
            print(f"✓ Traducido: {es[:50]}...")
        else:
            # Probar con texto multilínea
            es_lines = es.split('\n')
            if len(es_lines) > 1:
                # Construir patrón para texto multilínea
                msgid_lines = []
                for i, line in enumerate(es_lines):
                    if i == 0:
                        msgid_lines.append(f'msgid "{line}\\n"')
                    elif i == len(es_lines) - 1:
                        msgid_lines.append(f'"{line}"')
                    else:
                        msgid_lines.append(f'"{line}\\n"')
                
                patron_multilinea = '\n'.join(msgid_lines) + '\nmsgstr ""'
                
                # Construir reemplazo multilínea
                en_lines = en.split('\n')
                reemplazo_lines = []
                for i, line in enumerate(en_lines):
                    if i == 0:
                        reemplazo_lines.append(f'msgstr "{line}\\n"')
                    elif i == len(en_lines) - 1:
                        reemplazo_lines.append(f'"{line}"')
                    else:
                        reemplazo_lines.append(f'"{line}\\n"')
                
                reemplazo_multilinea = '\n'.join(msgid_lines) + '\n' + '\n'.join(reemplazo_lines)
                
                if patron_multilinea in contenido:
                    contenido = contenido.replace(patron_multilinea, reemplazo_multilinea)
                    print(f"✓ Traducido (multilínea): {es[:50]}...")
                else:
                    print(f"✗ No encontrado: {es[:50]}...")
            else:
                print(f"✗ No encontrado: {es[:50]}...")
    
    # Escribir el archivo actualizado
    with open('app/translations/en/LC_MESSAGES/messages.po', 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("\n¡Traducciones actualizadas!")

if __name__ == "__main__":
    actualizar_traducciones()
