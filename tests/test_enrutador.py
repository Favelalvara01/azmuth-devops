"""Pruebas del enrutador de skills (skills/__init__.py): la primera skill
que contesta gana, y el orden importa (aplicaciones SIEMPRE al final)."""
import pytest
import skills


def test_aplicaciones_y_apps_instaladas_van_al_final_de_la_lista():
    assert skills.SKILLS[-2].__name__.endswith(".aplicaciones")
    assert skills.SKILLS[-1].__name__.endswith(".apps_instaladas")


@pytest.mark.parametrize("frase,skill_esperada", [
    ("qué hora es", "tiempo"),
    ("toma nota: comprar café", "notas"),
    ("recuérdame comprar pan", "recordatorios"),
    ("recuerda que mi proyecto se llama Chispa", "memoria"),
    ("guarda el contacto de Jesús como 6561234567", "contactos"),
    ("mis hábitos", "habitos"),
    ("busca gatos", "web"),
    ("volumen a 40", "multimedia"),
    ("ayuda", "ayuda"),
    ("abre calculadora", "aplicaciones"),
    ("borra el historial", "sistema"),
])
def test_cada_frase_llega_a_su_skill(frase, skill_esperada):
    respuesta, skill = skills.procesar(frase)
    assert respuesta is not None
    assert skill == skill_esperada


def test_frase_desconocida_regresa_none_para_ir_a_claude():
    assert skills.procesar("cuéntame un chiste de programadores") == (None, None)


# Regresión DEF-011 (corregido en el Sprint 9)
def test_youtube_con_palabra_manual_no_debe_abrir_la_ayuda():
    _, skill = skills.procesar("abre youtube y busca manual de guitarra")
    assert skill == "aplicaciones"


# Regresión DEF-012 (corregido en el Sprint 9)
def test_pon_mi_playlist_lo_resuelve_una_skill():
    respuesta, _ = skills.procesar("pon mi playlist")
    assert respuesta is not None


@pytest.mark.parametrize("frase", ["ayuda", "¿Qué puedes hacer?", "dime tus comandos", "manual", "Azmuth, ayuda"])
def test_la_ayuda_sigue_respondiendo_a_peticiones_reales(frase):
    _, skill = skills.procesar(frase)
    assert skill == "ayuda"


def test_siguiente_a_secas_sigue_siendo_multimedia():
    _, skill = skills.procesar("siguiente")
    assert skill == "multimedia"


def test_la_sugerencia_de_habitos_ya_se_ejecuta():
    from skills import habitos
    respuesta, skill = skills.procesar(habitos.ACCION_SUGERIDA["multimedia"])
    assert skill == "aplicaciones" and respuesta == "Activando tu playlist"
