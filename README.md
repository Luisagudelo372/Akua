# Porvoz

Plataforma para mejorar el cumplimiento de medicamentos mediante recordatorios automáticos por llamadas de voz.

## El Problema

Entre el 30-50% de los pacientes con enfermedades crónicas no toman sus medicamentos a tiempo. Las notificaciones por app no funcionan bien con adultos mayores. Los cuidadores no pueden supervisar constantemente.

## La Solución

Porvoz registra medicamentos con horarios específicos y realiza llamadas automáticas para recordar al paciente cuándo tomar cada medicamento. El sistema verifica si respondió y alerta al cuidador si hay falta de cumplimiento.

## Características

- **Registro de Pacientes:** Crea perfiles para ti o para personas a tu cargo
- **Gestión de Medicamentos:** Registra medicamentos con dosis y múltiples horarios al día
- **Condiciones Médicas:** Mantén un historial de las condiciones de cada paciente
- **Notificaciones:** Recibe alertas sobre medicamentos tomados o no tomados
- **Edición de Perfil:** Actualiza tus datos personales y contacto de emergencia
- **Guía Integrada:** Accede a ayuda desde el dashboard

## Instalación

### Requisitos
- Python 3.10+
- pip

### Pasos

```bash
# Clonar repositorio
git clone https://github.com/Porvoz/Porvoz_web.git
cd porvoz

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
python manage.py migrate

# Crear usuario administrador
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

Accede a `http://localhost:8000` en tu navegador.

## Uso

1. **Registrarse:** Crea una cuenta con tu correo
2. **Agregar Paciente:** Registra a la persona que necesita recordatorios
3. **Agregar Medicamento:** Define qué medicamento, dosis y a qué hora
4. **Ver Notificaciones:** Consulta el estado de los medicamentos
5. **Editando:** Cambia horarios, pausa medicamentos o agrega nuevas condiciones

## Stack Tecnológico

- **Backend:** Django 5.2
- **Base de Datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend:** HTML + Tailwind CSS + Bootstrap Icons
- **Autenticación:** Django Auth

## Estructura del Proyecto

```
porvoz/
├── apps/                    # Módulos funcionales
│   ├── autenticacion/       # Registro e inicio de sesión
│   ├── usuarios/            # Gestión de perfil
│   ├── pacientes/           # Gestión de pacientes
│   ├── medicamentos/        # Gestión de medicamentos
│   ├── notificaciones/      # Sistema de notificaciones
│   └── core/                # Funcionalidades compartidas
├── templates/               # Plantillas HTML
├── static/                  # Imágenes y assets
└── config/                  # Configuración de Django
```


## Equipo

### Integrantes del Desarrollo
- Luis Alfonso Agudelo Ramírez
- Julián Lara Aristizabal
- Matías Martínez Moreno
- Nathalia Cardoza
- Samuel Samper

### Product Owners
- Mateo Zacar
- Styven Bedoya
