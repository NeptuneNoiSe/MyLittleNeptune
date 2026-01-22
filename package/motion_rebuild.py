import json
import os
import resources
from pathlib import Path


def auto_convert_parameter_name(old_name):
    """
    Автоматически преобразует имена параметров по шаблону:
    "PARAM_ANGLE_X" -> "ParamAngleX"
    "PARAM_EYE_BALL_Y" -> "ParamEyeBallY"
    """
    if old_name.startswith("PARAM_") and "_" in old_name:
        # Преобразуем "PARAM_ANGLE_X" -> "ParamAngleX"
        parts = old_name.split("_")[1:]  # Убираем "PARAM"
        converted = "Param" + "".join(part.capitalize() for part in parts if part)
        return converted
    return old_name  # Если не наш шаблон - оставляем как есть


def convert_parameters_in_motion(motion: dict) -> int:
    """
    Преобразует имена параметров в motion и возвращает количество изменений
    """
    changed_count = 0
    if "Curves" in motion:
        for curve in motion["Curves"]:
            if curve["Target"] == "Parameter":
                old_id = curve["Id"]
                new_id = auto_convert_parameter_name(old_id)
                if old_id != new_id:
                    curve["Id"] = new_id
                    changed_count += 1
    return changed_count


def recount_motion(motion: dict) -> tuple[int, int, int]:
    """
    重新计算*.motion3.json文件中curveCount, TotalSegmentCount和TotalPointCount的值
    """
    segment_count = 0
    point_count = 0
    curves = motion["Curves"]
    curve_count = len(curves)
    for curve in curves:
        segments = curve["Segments"]
        end_pos = len(segments)
        point_count += 1
        v = 2
        while v < end_pos:
            identifier = segments[v]
            if identifier == 0 or identifier == 2 or identifier == 3:
                point_count += 1
                v += 3
            elif identifier == 1:
                point_count += 3
                v += 7
            else:
                raise Exception("unknown identifier: %d" % identifier)
            segment_count += 1
    return curve_count, segment_count, point_count


def load_all_motion_path_from_model_dir(model_dir: str) -> list[str]:
    """导入模型文件夹中所有的motion3.json文件*路径*"""
    # Пробуем разные варианты папок
    possible_dirs = [
        os.path.join(model_dir, "motions"),
        os.path.join(model_dir, "motion"),
        os.path.join(model_dir, "Motions"),
        os.path.join(model_dir, "Motion")
    ]

    motions_dir = None
    for dir_path in possible_dirs:
        if os.path.exists(dir_path):
            motions_dir = dir_path
            break

    if motions_dir is None:
        return []  # Ни одна папка не найдена

    ls = list()
    for filename in os.listdir(motions_dir):
        if filename.endswith(".motion3.json"):
            ls.append(os.path.join(motions_dir, filename))

    return ls


def load_motion_from_path(path: str) -> dict:
    """通过motion3.json文件的路径导入"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def copy_modify_from_motion(motion_path: str, save_root: str = "./out/motions", convert_params: bool = True) -> None:
    """
    加载motion3.json文件, 重新计算并修改CurveCount, TotalSegmentCount和TotalPointCount的值,
    可选: преобразует имена параметров, 并导出新的motion3.json文件
    """
    motion = load_motion_from_path(motion_path)

    # Преобразование параметров (если нужно)
    param_changes = 0
    if convert_params:
        param_changes = convert_parameters_in_motion(motion)

    # Пересчет метаданных
    curve_count, segment_count, point_count = recount_motion(motion)
    motion["Meta"]["CurveCount"] = curve_count
    motion["Meta"]["TotalSegmentCount"] = segment_count
    motion["Meta"]["TotalPointCount"] = point_count

    # Сохранение
    if not os.path.exists(save_root):
        os.makedirs(save_root)

    output_path = os.path.join(save_root, os.path.basename(motion_path))
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(motion, f, indent=2, ensure_ascii=False)

    return param_changes


def process_model_motions(model_name: str, convert_params: bool = True):
    """
    Обрабатывает все motion файлы для указанной модели
    """
    model_path = os.path.join(resources.RESOURCES_DIRECTORY, "models", model_name)
    motion_paths = load_all_motion_path_from_model_dir(model_path)

    if not motion_paths:
        print(f"⚠️ Не найдено motion файлов для модели: {model_name}")
        return

    total_changes = 0
    total_files = len(motion_paths)

    print(f"🔧 Обработка модели: {model_name}")
    print(f"📁 Найдено файлов: {total_files}")

    for i, path in enumerate(motion_paths, 1):
        try:
            changes = copy_modify_from_motion(
                path,
                save_root=f"./fixed_motions/{model_name}/motions",
                convert_params=convert_params
            )
            total_changes += changes
            print(f"  [{i}/{total_files}] {os.path.basename(path)}: {changes} изменений параметров")
        except Exception as e:
            print(f"  ❌ Ошибка в {os.path.basename(path)}: {e}")

    print(f"✅ Готово! Всего изменений параметров: {total_changes}")


def preview_model_conversions(model_name: str):
    """
    Предпросмотр преобразований для модели
    """
    model_path = os.path.join(resources.RESOURCES_DIRECTORY, "models", model_name)
    motion_paths = load_all_motion_path_from_model_dir(model_path)

    conversions = set()

    for path in motion_paths:
        try:
            motion = load_motion_from_path(path)
            if "Curves" in motion:
                for curve in motion["Curves"]:
                    if curve["Target"] == "Parameter":
                        old_id = curve["Id"]
                        new_id = auto_convert_parameter_name(old_id)
                        if old_id != new_id:
                            conversions.add((old_id, new_id))
        except:
            continue

    print(f"🔍 Преобразования для модели '{model_name}':")
    for old, new in sorted(conversions):
        print(f"  {old} -> {new}")


if __name__ == "__main__":
    # Пример использования:

    # 1. Предпросмотр преобразований
    # preview_model_conversions("Neptune")

    # 2. Обработка с преобразованием параметров
    process_model_motions("Neptune", convert_params=True)

    # 3. Обработка БЕЗ преобразования параметров (только пересчет метаданных)
    # process_model_motions("Neptune", convert_params=False)