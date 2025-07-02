# 🧮 MOPSolver - Linear Programming Solver

**MOPSolver** es una aplicación web Flask para resolver problemas de programación lineal con múltiples métodos (SciPy, Simplex Clásico, Gran M). Incluye autenticación de usuarios, historial de problemas, internacionalización (español/inglés) y sistema de temas dinámico con Daisy UI + Tailwind CSS.

## 📋 Características

- ✅ Resolución de problemas de programación lineal
- ✅ Múltiples métodos de solución (SciPy, Simplex, Gran M)
- ✅ Sistema de usuarios con autenticación
- ✅ Historial de problemas resueltos
- ✅ Interfaz multiidioma (Español/Inglés)
- ✅ Temas dinámicos (Light, Dark, Cupcake, Business)
- ✅ Diseño responsive con Tailwind CSS + Daisy UI
- ✅ Análisis de sensibilidad y variables de holgura

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask**: Framework web principal
- **Flask-Login**: Autenticación de usuarios
- **Flask-Babel**: Internacionalización
- **SciPy**: Resolución optimizada de problemas LP
- **NumPy**: Cálculos matemáticos
- **Pandas**: Manipulación de datos

### Frontend
- **Tailwind CSS**: Framework CSS utility-first
- **Daisy UI**: Biblioteca de componentes UI
- **Font Awesome**: Iconografía
- **Notyf**: Notificaciones toast
- **JavaScript Vanilla**: Interactividad

## 📁 Estructura del Proyecto

```
Mop_Project/
├── app/
│   ├── __init__.py
│   ├── routes.py              # Rutas principales
│   ├── models.py              # Modelos de usuario
│   ├── helpers.py             # Funciones auxiliares
│   ├── solver.py              # Solver principal (SciPy)
│   ├── simplex_solver.py      # Solver Simplex clásico
│   ├── test.py                # Solver Gran M
│   ├── extensions.py          # Extensiones y utilidades
│   ├── static/
│   │   ├── js/
│   │   │   ├── base.js
│   │   │   ├── i18n.js
│   │   │   ├── index.js
│   │   │   ├── mathInput.js
│   │   │   ├── simplexSolver.js
│   │   │   └── solver.js
│   │   └── styles/
│   │       ├── base.css       # CSS base + imports
│   │       └── tailwind.css   # CSS compilado (generado)
│   ├── templates/             # Templates Jinja2
│   ├── translations/          # Archivos de traducción
│   └── babel_config/          # Configuración Babel
├── data/                      # Datos de usuarios e historial
├── package.json               # Dependencias Node.js
├── requirements.txt           # Dependencias Python
├── run.py                     # Punto de entrada
└── README.md
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- **Python 3.8+**
- **Node.js 16+** y **npm**
- **Git**

### 📥 Clonar el Repositorio

```bash
git clone https://github.com/JefersonDeLaCruz/Mop_Project.git
cd Mop_Project
```

---

## 🪟 Instalación en Windows

### 1. Crear y Activar Entorno Virtual Python

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Verificar activación (debe mostrar (venv) al inicio)
```

### 2. Instalar Dependencias Python

```powershell
# Instalar todas las dependencias
pip install -r requirements.txt

# Verificar instalación
pip list
```

### 3. Instalar Dependencias Node.js

```powershell
# Instalar dependencias del package.json
npm install

# Instalar Tailwind CSS CLI (si no está incluido)
npm install tailwindcss @tailwindcss/cli
```

### 4. Compilar CSS de Tailwind

```powershell
# Compilar CSS una vez
npm run swag

# O compilar en modo watch (recomendado para desarrollo)
npx tailwindcss -i ./app/static/styles/base.css -o ./app/static/styles/tailwind.css --watch
```

### 5. Crear Directorio de Datos

```powershell
# Crear directorio para datos de usuarios
mkdir data
```

### 6. Ejecutar la Aplicación

```powershell
# Ejecutar servidor de desarrollo
python run.py

# La aplicación estará disponible en: http://localhost:5000
```

---

## 🐧 Instalación en Linux/macOS

### 1. Crear y Activar Entorno Virtual Python

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Verificar activación (debe mostrar (venv) al inicio)
```

### 2. Instalar Dependencias Python

```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# Verificar instalación
pip list
```

### 3. Instalar Dependencias Node.js

```bash
# Instalar dependencias del package.json
npm install

# Instalar Tailwind CSS CLI (si no está incluido)
npm install tailwindcss @tailwindcss/cli
```

### 4. Compilar CSS de Tailwind

```bash
# Compilar CSS una vez
npm run swag

# O compilar en modo watch (recomendado para desarrollo)
npx tailwindcss -i ./app/static/styles/base.css -o ./app/static/styles/tailwind.css --watch
```

### 5. Crear Directorio de Datos

```bash
# Crear directorio para datos de usuarios
mkdir -p data
```

### 6. Ejecutar la Aplicación

```bash
# Ejecutar servidor de desarrollo
python run.py

# La aplicación estará disponible en: http://localhost:5000
```

---

## ⚙️ Scripts Disponibles

### Python

```bash
# Ejecutar aplicación
python run.py

# Actualizar traducciones (si modificas textos)
python actualizar_traducciones.py
```

### Node.js

```bash
# Compilar CSS de Tailwind (una vez)
npm run swag

# Compilar CSS en modo watch
npx tailwindcss -i ./app/static/styles/base.css -o ./app/static/styles/tailwind.css --watch

# Instalar dependencias
npm install
```

## 🎨 Sistema de Temas

La aplicación incluye 4 temas predefinidos:

- **Light**: Tema claro predeterminado
- **Dark**: Tema oscuro
- **Cupcake**: Tema suave y pastel
- **Business**: Tema empresarial

Los temas se cambian dinámicamente desde el navbar y se persisten en localStorage.

## 🌍 Idiomas Soportados

- **Español** (es) - Predeterminado
- **English** (en)

### Actualizar Traducciones

Si modificas textos en los templates, ejecuta:

```bash
python actualizar_traducciones.py
```

## 📊 Métodos de Resolución

1. **SciPy** (Recomendado): Rápido y eficiente para problemas grandes
2. **Simplex Clásico**: Educativo, muestra pasos intermedios
3. **Gran M**: Para problemas con restricciones de igualdad o ≥

## 🔐 Autenticación

- Los usuarios se almacenan en `data/usuarios.json`
- Las contraseñas se hashean con bcrypt
- El historial de cada usuario se guarda en `data/{user_id}_historial.json`

## 🚨 Solución de Problemas

### ❌ Error: "tailwind.css not found"

```bash
# Compilar CSS de Tailwind
npm run swag
```

### ❌ Error: "Module 'flask' not found"

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### ❌ Error: "npm command not found"

Instala Node.js desde [nodejs.org](https://nodejs.org/)

### ❌ Error: "Permission denied" (Linux)

```bash
# Dar permisos de ejecución
chmod +x run.py
```

### ❌ CSS no se actualiza

```bash
# Limpiar cache del navegador (Ctrl+F5)
# O ejecutar compilación forzada
npx tailwindcss -i ./app/static/styles/base.css -o ./app/static/styles/tailwind.css --watch
```

## 📝 Uso de la Aplicación

### 1. Registro/Login
- Crea una cuenta o inicia sesión
- Los datos se almacenan localmente en `data/`

### 2. Resolver Problemas
- Ve a "Nuevo Problema"
- Selecciona Maximizar/Minimizar
- Ingresa función objetivo: `3x1 + 2x2`
- Agrega restricciones: `2x1 + x2 <= 10`
- Elige método de resolución
- Haz clic en "Resolver"

### 3. Ver Historial
- Accede desde tu perfil o el menú "Historial"
- Filtra por tipo de problema
- Ve detalles completos de cada solución

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit tus cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia ISC. Ver archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Jeferson De La Cruz**
- GitHub: [@JefersonDeLaCruz](https://github.com/JefersonDeLaCruz)
- Proyecto: [Mop_Project](https://github.com/JefersonDeLaCruz/Mop_Project)

---

## 📞 Soporte

Si tienes problemas con la instalación o ejecución:

1. Verifica que tengas Python 3.8+ y Node.js 16+
2. Asegúrate de que el entorno virtual esté activado
3. Compila el CSS de Tailwind con `npm run swag`
4. Revisa que el directorio `data/` exista

**¡Disfruta resolviendo problemas de programación lineal! 🎯**
