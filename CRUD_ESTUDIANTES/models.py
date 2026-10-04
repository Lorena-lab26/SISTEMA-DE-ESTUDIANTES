import json
CAMPOS_ESTUDIANTE = ("nombre", "apellido", "email", "carnet")

class Estudiante:
    def __init__(self, id, nombre, apellido, email, carnet, notas=None, materias=None):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.carnet = carnet
        # DICCIONARIO para almacenar notas por materia: {"Matemática": [18, 19], ...}
        self.notas = notas if notas is not None else {}
        # CONJUNTO (set) para garantizar materias únicas inscritas
        self.materias = set(materias) if materias is not None else set()

    def obtener_nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def calcular_promedio(self):
        todas_las_notas = []
        for lista_notas in self.notas.values():
            todas_las_notas.extend(lista_notas)
        if not todas_las_notas:
            return 0.0
        return sum(todas_las_notas) / len(todas_las_notas)

    def a_diccionario(self):
        """Convierte la instancia a diccionario serializable a JSON."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "carnet": self.carnet,
            "notas": self.notas,
            # Se convierte el SET a LISTA para compatibilidad con JSON
            "materias": sorted(list(self.materias))
        }

    @classmethod
    def desde_diccionario(cls, datos):
        """Crea una instancia de Estudiante convirtiendo la lista de materias de nuevo a SET."""
        return cls(
            id=datos["id"],
            nombre=datos["nombre"],
            apellido=datos["apellido"],
            email=datos["email"],
            carnet=datos["carnet"],
            notas=datos.get("notas", {}),
            # Convierte la LISTA del JSON nuevamente a CONJUNTO (set)
            materias=set(datos.get("materias", []))
        )

    def __str__(self):
        return f"[{self.id}] {self.obtener_nombre_completo()} - Carnet: {self.carnet}"