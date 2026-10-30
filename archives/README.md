# Полный пакет PEGASUS Frost Arsenal

[PEGASUS_Frost_Arsenal_FULL.zip](PEGASUS_Frost_Arsenal_FULL.zip) — около 373 МиБ, хранится в **Git LFS**. На странице файла GitHub выберите скачивание исходного файла. Контрольная сумма полного архива находится рядом в `PEGASUS_Frost_Arsenal_FULL.zip.sha256`.

Включены 12 GLB, 12 редактируемых Blender-сцен, 12 исходных OBJ Valve Workshop, новые текстуры и рендеры, исходный код, тестовая DLL трассеров, инструкции и два видеореференса. Внутри есть `README_RU.txt`, `PACKAGE.json` и контрольные суммы файлов `SHA256SUMS.txt`.

Для получения через Git:

```bash
git lfs install
git clone --branch feat/winter-arsenal-prototypes https://github.com/andrey020215-ctrl/Guns1.git
cd Guns1
git lfs pull
```

Если файл оказался небольшим текстовым указателем `version https://git-lfs.github.com/spec/v1`, LFS-данные не загружены: выполните `git lfs pull`. ZIP исходников, автоматически создаваемый GitHub, может содержать указатель; скачивайте сам полный архив или используйте Git LFS.

**Тестовый статус:** сборка CounterStrikeSharp.API 1.0.378 / .NET 10 и 121 автопроверка трассеров пройдены. Интеграция выдачи/материалов и проверка в CS2 не завершены; это не готовая установка на сервер. Подробности — `docs/ICY_TRACERS.md`.
