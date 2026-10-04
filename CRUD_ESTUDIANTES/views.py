import json
import os
from models import Estudiante

RUTA_JSON = os.path.join("data", "estudiantes.json")


def _cargar_datos():
    """Carga los estudiantes desde el archivo JSON."""
    if not os.path.exists(RUTA_JSON):
        return []
    try:
        with open(RUTA_JSON, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            return [Estudiante.desde_diccionario(item) for item in datos]
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _guardar_datos(estudiantes):
    """Guarda la lista de estudiantes en el archivo JSON."""
    os.makedirs(os.path.dirname(RUTA_JSON), exist_ok=True)
    with open(RUTA_JSON, "w", encoding="utf-8") as archivo:
        datos = [est.a_diccionario() for est in estudiantes]
        json.dump(datos, archivo, indent=2, ensure_ascii=False)


# ---------- OPERACIONES CRUD Y LÓGICA DE NEGOCIO ----------

def crear_estudiante(datos):
    estudiantes = _cargar_datos()

    # Validación de carnet y email únicos utilizando CONJUNTOS (sets)
    carnets_existentes = {est.carnet.upper() for est in estudiantes}
    emails_existentes = {est.email.lower() for est in estudiantes}

    if datos.get("carnet", "").upper() in carnets_existentes:
        return False, "El número de carnet ya se encuentra registrado."

    if datos.get("email", "").lower() in emails_existentes:
        return False, "El correo electrónico ya se encuentra registrado."

    # Generación de ID autoincremental
    nuevo_id = max([est.id for est in estudiantes], default=0) + 1

    nuevo_estudiante = Estudiante(
        id=nuevo_id,
        nombre=datos.get("nombre", ""),
        apellido=datos.get("apellido", ""),
        email=datos.get("email", ""),
        carnet=datos.get("carnet", "")
    )

    estudiantes.append(nuevo_estudiante)
    _guardar_datos(estudiantes)
    return True, f"Estudiante '{nuevo_estudiante.obtener_nombre_completo()}' creado exitosamente con ID {nuevo_id}."


def obtener_todos():
    return _cargar_datos()


def obtener_por_id(id_estudiante):
    estudiantes = _cargar_datos()
    for est in estudiantes:
        if est.id == id_estudiante:
            return est
    return None


def buscar_estudiantes(termino):
    termino_lower = termino.lower()
    estudiantes = _cargar_datos()
    encontrados = []
    for est in estudiantes:
        if (termino_lower in est.nombre.lower() or
            termino_lower in est.apellido.lower() or
            termino_lower in est.email.lower() or
            termino_lower in est.carnet.lower()):
            encontrados.append(est)
    return encontrados


def actualizar_estudiante(id_estudiante, cambios):
    estudiantes = _cargar_datos()
    estudiante = None
    for est in estudiantes:
        if est.id == id_estudiante:
            estudiante = est
            break

    if not estudiante:
        return False, f"No existe un estudiante con el ID {id_estudiante}."

    # Validar duplicados de carnet o email si se intentan modificar
    if "carnet" in cambios:
        carnets = {e.carnet.upper() for e in estudiantes if e.id != id_estudiante}
        if cambios["carnet"].upper() in carnets:
            return False, "El nuevo carnet ya pertenece a otro estudiante."

    if "email" in cambios:
        emails = {e.email.lower() for e in estudiantes if e.id != id_estudiante}
        if cambios["email"].lower() in emails:
            return False, "El nuevo email ya pertenece a otro estudiante."

    for campo, valor in cambios.items():
        if hasattr(estudiante, campo):
            setattr(estudiante, campo, valor)

    _guardar_datos(estudiantes)
    return True, "Estudiante actualizado correctamente."


def eliminar_estudiante(id_estudiante):
    estudiantes = _cargar_datos()
    filtrados = [est for est in estudiantes if est.id != id_estudiante]

    if len(filtrados) == len(estudiantes):
        return False, f"No existe el estudiante con ID {id_estudiante}."

    _guardar_datos(filtrados)
    return True, "Estudiante eliminado exitosamente."


def agregar_nota(id_estudiante, materia, nota):
    """Valida la nota (0-20), registra el puntaje y agrega la materia al SET del estudiante."""
    if not (0 <= nota <= 20):
        return False, "La nota debe ser un número entero o decimal entre 0 y 20."

    estudiantes = _cargar_datos()
    estudiante = None
    for est in estudiantes:
        if est.id == id_estudiante:
            estudiante = est
            break

    if not estudiante:
        return False, f"No se encontró ningún estudiante con el ID {id_estudiante}."

    materia_clean = materia.strip().capitalize()

    # Si la materia no existe en el diccionario del estudiante, se crea su lista
    if materia_clean not in estudiante.notas:
        estudiante.notas[materia_clean] = []

    estudiante.notas[materia_clean].append(nota)
    # Se añade la materia al CONJUNTO (set) del estudiante
    estudiante.materias.add(materia_clean)

    _guardar_datos(estudiantes)
    return True, f"Nota {nota} añadida a la materia '{materia_clean}' para {estudiante.obtener_nombre_completo()}."


def materias_ofertadas():
    """Devuelve un CONJUNTO (set) con todas las materias registradas en el sistema."""
    estudiantes = _cargar_datos()
    todas_las_materias = set()
    for est in estudiantes:
        # Unión de conjuntos
        todas_las_materias.update(est.materias)
    return todas_las_materias


def estudiantes_en_comun(id_a, id_b):
    """Obtiene la intersección de materias entre dos estudiantes."""
    est_a = obtener_por_id(id_a)
    est_b = obtener_por_id(id_b)

    if not est_a or not est_b:
        return None, "Uno o ambos IDs ingresados no existen."

    # Intersección de CONJUNTOS (set)
    materias_comunes = est_a.materias.intersection(est_b.materias)
    return materias_comunes, f"Materias en común entre {est_a.nombre} y {est_b.nombre}."


def estadisticas():
    estudiantes = _cargar_datos()
    total = len(estudiantes)
    materias = materias_ofertadas()
    promedios = [est.calcular_promedio() for est in estudiantes if est.calcular_promedio() > 0]
    promedio_general = sum(promedios) / len(promedios) if promedios else 0.0

    return {
        "total": total,
        "materias": materias,
        "promedio_general": round(promedio_general, 2)
    }