# Tasks

## 1. Общий фронтенд-паттерн

- [x] 1.1 Добавлен переиспользуемый компонент `src/components/ExpandableItem.tsx` (кнопка-заголовок с `aria-expanded` + шеврон `rotate-180`, тело при раскрытии, слот `actions` для кнопок строки, коллбэк `onToggle` для ленивой загрузки).
- [x] 1.2 Состояние диалога сущности — union (`{ mode: "create" } | { mode: "edit", … } | null`) на каждой странице; состояние удаления — отдельный target.
- [x] 1.3 Используются существующие `components/Modal.tsx` и `components/DeleteConfirmModal.tsx`; вендоренные файлы не тронуты.

## 2. Backend: полнота CRUD

- [x] 2.1 `app/api/routes/owners.py`: `DELETE /{id}` с `409` при ссылках (`count_references` по `measuring_instruments`/`protocols`), `PUT /{id}/aliases` (полная замена). `OwnerOut` теперь отдаёт `aliases`; `OwnerRepository.list_all/get_by_id` грузят алиасы.
- [x] 2.2 `app/api/routes/methodologies.py`: `DELETE /{id}` с `409`, `PUT /{id}/aliases`; `MethodologyOut` отдаёт `aliases` (`replace_aliases`, `count_references`).
- [x] 2.3 `app/api/routes/etalons.py`: `PATCH /{id}`, `DELETE /{id}` (со свидетельствами), `GET/POST /{id}/certifications`, `DELETE /{id}/certifications/{cid}`; схемы `EtalonUpdate`, `EtalonCertificationIn/Out`.
- [x] 2.4 `app/api/routes/auxiliary_instruments.py`: `PATCH /{id}` (перенормализует серийник), `DELETE /{id}`.
- [x] 2.5 Тесты роутеров добавлены (`tests/test_reference_crud_routes.py`): алиасы и удаление владельца, алиасы и удаление методики, `PATCH`/`DELETE` вспом. СИ, `PATCH`/`DELETE` эталона со свидетельствами. *(прогон `pytest` — на сервере; отказ `409` требует ссылающейся записи и проверяется вручную)*

## 3. Frontend: справочники

- [x] 3.1 `AdminOwnersPage.tsx`: карточки-аккордеоны, создание/правка в `Modal`, удаление через `DeleteConfirmModal`, алиасы в диалоге.
- [x] 3.2 `AdminMethodologiesPage.tsx`: карточки-аккордеоны; диалог создания/правки (`createMethodology` добавлен в API-клиент) с редактором пунктов и алиасами; удаление.
- [x] 3.3 `AdminEtalonsPage.tsx`: карточки-аккордеоны; диалог создания/правки; список свидетельств с добавлением/удалением; удаление эталона.
- [x] 3.4 `AdminAuxInstrumentsPage.tsx`: карточки-аккордеоны; диалог создания/правки; удаление.
- [x] 3.5 Ошибки показываются внутри диалога (`saveMutation.isError`, `errorMessage` в `DeleteConfirmModal`), успех инвалидирует запросы и закрывает диалог.

## 4. Frontend: реестр генерации

- [x] 4.1 `GenerationPage.tsx` (зона «База данных»): строка реестра раскрывается кнопкой (шеврон), под ней отдельный `<tr colSpan=9>` с деталями (тип прибора, лист, номер протокола, действителен до, строка в файле, источник, загружено).
- [x] 4.2 Поиск, фильтры и «Активные» работают как раньше — раскрытие не меняет запросы.

## 5. Проверка

- [x] 5.1 `cd frontend && npx tsc --noEmit` — зелёный.
- [x] 5.2 `cd frontend && npm run check:ui` — зелёный (28 вендоренных файлов, без хардкода цветов).
- [x] 5.3 `cd frontend && npm run build` — зелёный; `npm run lint` — 0 ошибок.
- [x] 5.4 Backend: `ruff check app/` — новых замечаний нет (те же 8 предсуществующих).
- [x] 5.5 Backend: новые роут-тесты прогнаны на сервере в одноразовом контейнере против staging-БД — 18/18 (`tests/test_reference_crud_routes.py`, `tests/test_template_rules.py`).
- [x] 5.6 API-сценарии проверены на stage (`metroGen_api_stg`): владелец (создание/алиасы/удаление), методика (создание/алиасы/удаление), вспом. СИ (создание/правка/удаление), эталон (правка/свидетельства/удаление). UI-прогон в браузере — за владельцем.
