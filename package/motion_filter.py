import json
import os
import resources
from pathlib import Path


def filter_parameters_in_motion(motion: dict, allowed_params: list) -> int:
    """
    Удаляет параметры которых нет в allowed_params и возвращает количество удаленных
    """
    removed_count = 0
    if "Curves" in motion:
        # Фильтруем curves, оставляя только разрешенные параметры
        filtered_curves = []
        for curve in motion["Curves"]:
            if curve["Target"] == "Parameter" and curve["Id"] in allowed_params:
                filtered_curves.append(curve)
            else:
                removed_count += 1

        motion["Curves"] = filtered_curves

    return removed_count


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
    # Пробуем найти папку с motion файлами
    for folder_name in ["motions", "motion", "Motions", "Motion"]:
        motions_dir = os.path.join(model_dir, folder_name)
        if os.path.exists(motions_dir):
            return [
                os.path.join(motions_dir, filename)
                for filename in os.listdir(motions_dir)
                if filename.endswith(".motion3.json")
            ]

    return []  # Папка не найдена


def load_motion_from_path(path: str) -> dict:
    """通过motion3.json文件的路径导入"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def process_motion_filtering(motion_path: str, allowed_params: list, save_root: str = "./filtered_motions") -> dict:
    """
    Фильтрует параметры в motion файле и сохраняет результат
    Возвращает статистику изменений
    """
    motion = load_motion_from_path(motion_path)

    # Сохраняем оригинальное количество curves
    original_count = len(motion["Curves"]) if "Curves" in motion else 0

    # Фильтруем параметры
    removed_count = filter_parameters_in_motion(motion, allowed_params)

    # Пересчитываем метаданные
    curve_count, segment_count, point_count = recount_motion(motion)
    motion["Meta"]["CurveCount"] = curve_count
    motion["Meta"]["TotalSegmentCount"] = segment_count
    motion["Meta"]["TotalPointCount"] = point_count

    # Сохраняем результат
    if not os.path.exists(save_root):
        os.makedirs(save_root)

    output_path = os.path.join(save_root, os.path.basename(motion_path))
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(motion, f, indent=2, ensure_ascii=False)

    return {
        "filename": os.path.basename(motion_path),
        "original_curves": original_count,
        "removed_curves": removed_count,
        "remaining_curves": curve_count
    }


def filter_model_motions(model_name: str, allowed_params: list):
    """
    Фильтрует параметры во всех motion файлах указанной модели
    """
    model_path = os.path.join(resources.RESOURCES_DIRECTORY, "models", model_name)
    motion_paths = load_all_motion_path_from_model_dir(model_path)

    if not motion_paths:
        print(f"⚠️ Не найдено motion файлов для модели: {model_name}")
        return

    total_removed = 0
    total_original = 0
    total_files = len(motion_paths)

    print(f"🔧 Фильтрация модели: {model_name}")
    print(f"📁 Найдено файлов: {total_files}")
    print(f"✅ Разрешенные параметры: {allowed_params}")
    print("-" * 50)

    for i, path in enumerate(motion_paths, 1):
        try:
            stats = process_motion_filtering(
                path,
                allowed_params,
                save_root=f"./filtered_motions/{model_name}/motions"
            )

            total_original += stats["original_curves"]
            total_removed += stats["removed_curves"]

            print(f"  [{i}/{total_files}] {stats['filename']}:")
            print(f"     Удалено: {stats['removed_curves']}")
            print(f"     Осталось: {stats['remaining_curves']}")

        except Exception as e:
            print(f"  ❌ Ошибка в {os.path.basename(path)}: {e}")

    print("-" * 50)
    print(f"📊 Итоги для модели '{model_name}':")
    print(f"   Всего curves: {total_original}")
    print(f"   Удалено curves: {total_removed}")
    print(f"   Сохранено curves: {total_original - total_removed}")
    print(f"   Процент удаления: {(total_removed / total_original * 100):.1f}%")


def find_all_parameters_in_model(model_name: str) -> set:
    """
    Находит все уникальные параметры в motion файлах модели
    """
    model_path = os.path.join(resources.RESOURCES_DIRECTORY, "models", model_name)
    motion_paths = load_all_motion_path_from_model_dir(model_path)

    all_params = set()

    for path in motion_paths:
        try:
            motion = load_motion_from_path(path)
            if "Curves" in motion:
                for curve in motion["Curves"]:
                    if curve["Target"] == "Parameter":
                        all_params.add(curve["Id"])
        except:
            continue

    return sorted(all_params)


if __name__ == "__main__":
    # 1. Список разрешенных параметров (настрой под себя)
    ALLOWED_PARAMETERS = [
        'ParamAngleX',
        'ParamAngleY',
        'ParamAngleZ',
        'ParamEyeLOpen',
        'ParamEyeROpen',
        'ParamMouthForm',
        'ParamBrowLY',
        'ParamBrowRY'
    ]

    # 2. Название модели для обработки
    MODEL_NAME = "Neptune"

    # 3. Предварительный просмотр всех параметров модели
    print("🔍 Все параметры модели:")
    all_params = find_all_parameters_in_model(MODEL_NAME)
    for param in all_params:
        status = "✅" if param in ALLOWED_PARAMETERS else "❌"
        print(f"  {status} {param}")

    print(f"\n🎯 Будут сохранены только: {ALLOWED_PARAMETERS}")

    # 4. Запуск фильтрации
    filter_model_motions(MODEL_NAME, ALLOWED_PARAMETERS)