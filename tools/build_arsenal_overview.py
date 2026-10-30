"""Build the full Russian overview and an offline HTML report with embedded render images."""
from pathlib import Path
import base64, html, json
ROOT=Path(__file__).resolve().parents[1]
load=lambda p:json.loads((ROOT/p).read_text())
catalog=load('config/vip_weapons.concept.json')
models=load('assets/frost_cs2/manifest.json')
model_by_id={x['id']:x for x in models}
tracer=load('assets/icy_tracers/validation.json')
GEOMETRY=load('assets/frost_cs2/validation.json')
assert len(catalog['weapons'])==len(models)==len(GEOMETRY['models'])==12
assert tracer['tracer_checks_passed']==121 and not tracer['cs2_tested']
GITHUB='https://github.com/andrey020215-ctrl/Guns1'
BRANCH='feat/winter-arsenal-prototypes'
ARCHIVE=GITHUB+'/blob/'+BRANCH+'/archives/PEGASUS_Frost_Arsenal_FULL.zip'
PR=GITHUB+'/pull/2'
VISUALS={
'mp9':'Красный фон, снегири, рябина, хвоя, снежинки и золотой орнамент.',
'famas':'Тёмно-зелёный еловой фон, золотая филигрань и светлые снежинки.',
'nova':'Сапфировый фон, серебристые снежинки и завитки, бирюзовые детали.',
'glock18':'Красно-зелёный рождественский орнамент, ягоды, хвоя и золотые завитки.',
'ak47':'Кобальтовый фон, серебристый морозный орнамент, бирюзовые и рубиновые акценты.',
'm4a1s':'Красно-зелёный еловой орнамент с золотыми деталями, в том числе на глушителе.',
'ssg08':'Бирюзово-синий орнамент, звёзды, золотая филигрань и Пегасы.',
'usp_s':'Фиолетово-серебристое зимнее кружево на корпусе и глушителе.',
'awp':'Сапфировые и серебристые узоры со снежинками на ложе, стволе и прицеле.',
'xm1014':'Гранатово-красный и фиолетовый орнамент, хвоя и золотые детали.',
'negev':'Малахитово-зелёная основа, золотой растительный орнамент и светлые снежинки.',
'deagle':'Сине-бирюзовый фон, белые Пегасы, звёзды, золото и фиолетовые детали.'}
FINISHES={1:('Иней','Бело-голубой перламутр','5 с'),2:('Метель','Голубые и бирюзовые прожилки','3,5 с'),3:('Аврора','Бирюзово-синие и фиолетовые волны северного сияния','4 с')}
weapons=[]
for index,w in enumerate(catalog['weapons']):
 m=model_by_id[w['id']]
 assert w['required_vip']==m['vip']
 weapons.append({**w,'render_name':m['reference_name'],'render':m['render'],'visual_now':VISUALS[w['id']],'index':index})
STATUS=[
('3D и текстуры','Созданы 12 моделей на официальной геометрии Valve Workshop: GLB, редактируемые Blender-сцены, исходные OBJ и цветовые карты 2048×2048.','Геометрия и исходные UV всех 12 моделей проверены. Игровые Source 2 ресурсы не скомпилированы.'),
('VIP и магазин','Есть проверяемая доменная политика доступа, покупки на одну карту и чтение локальных VIP-списков.','Роли PEGASUS, реальный баланс, игровые меню и выдача ещё не интегрированы.'),
('12 способностей','Условия, эффекты, ограничения и отдельные кулдауны описаны в каталоге.','Игровой AbilityEngine отсутствует; способности не реализованы в обработчиках CS2.'),
('Ледяные трассеры','Реализован и собран модуль с привязкой к конкретному экземпляру, владельцу/pawn и эпохе карты. Прошли 121 автопроверка.','Нужны регистрация реальной выдачи со скином, resolver дульной точки и согласование с Weapon Frost Effects; в CS2 не проверено.'),
('Переливы','В Blender есть мягкий автономный перелив в светлых деталях, с циклами коллекций.','GLB статический. Три полных Source 2 финиша и смена финиша по текущему VIP владельца не реализованы в игре.'),
('Сборка и сервер','Плагин собран на CounterStrikeSharp.API 1.0.378 / .NET 10 без ошибок и предупреждений.','Установленная версия API PEGASUS неизвестна. Сервер не изменялся, игровых тестов нет.')]
MATRIX=[('Обычный игрок',0,'Нет','Все 12 за снежинки'),('VIP I',4,'4 оружия коллекции I','Коллекции II и III'),('VIP II',8,'Коллекции I + II','Коллекция III'),('VIP III',12,'Все три коллекции','Все 12 уже разрешены бесплатно')]
md=['# PEGASUS — полный обзор зимнего арсенала','',
'**Фактический статус:** модели и текстуры созданы, модуль трассеров собран. Выдача, применение скинов и привязка к действующей системе ролей/экономики PEGASUS ещё не интегрированы. Все 12 суперспособностей пока являются спецификацией. Игровой тест CS2 не проводился.','',
'[Интерактивный HTML-обзор](../preview/winter-arsenal-overview.html) · [Полный архив в GitHub]('+ARCHIVE+') · [PR #2]('+PR+')','',
'## Что уже получилось','', '| Блок | Что создано | Что ещё требуется |','|---|---|---|']
md += ['| '+' | '.join(x)+' |' for x in STATUS]
md += ['', '## Все модели','', '![12 зимних оружий](../assets/frost_cs2/arsenal-cs2.jpg)','',
'Использована оригинальная геометрия официального пакета Valve CS2 Workshop. Новые орнаменты созданы по стилистике видеореференса, это не извлечённые текстуры видео. На рендерах стоят имена из видео; в игровом конфиге ещё сохранены прежние названия. Ниже они сопоставлены по ID, без изменения игровых параметров.','',
'## Привязка к трём уровням VIP','', '| Игрок | Бесплатных оружий | Бесплатный доступ по правилам | Остальное |','|---|---:|---|---|']
md += ['| '+' | '.join(map(str,x))+' |' for x in MATRIX]
md += ['', 'Эта матрица реализована в доменной логике, но ещё не подключена к настоящим ролям PEGASUS. `VipAccess` читает локальные списки по SteamID; реальные персональные списки в репозиторий не помещаются.','',
'## Магазин и выдача — правила','',
'- Все 12 оружий доступны обычному игроку за снежинки; VIP не является обязательным условием покупки.',
'- Предварительная цена одного предмета: коллекция I — **150**, II — **300**, III — **600 снежинок**.',
'- Покупка действует **до следующей смены карты**. Смерть, респавн и переподключение не отменяют право повторно взять купленный предмет.',
'- Повторное «Взять» не списывает деньги. При смене карты сбрасываются покупки, но не баланс снежинок.',
'- Используется существующая экономика PEGASUS; второй кошелёк не создаётся. Реальный адаптер баланса пока отсутствует.',
'- По проекту покупка и VIP «Взять» должны сразу выдавать и экипировать оружие в текущей жизни, с откатом при ошибке. Эта транзакция пока не реализована.',
'- Чат после покупки: «Вы купили <название> за N снежинок»; после успешной выдачи: «Вы взяли <название>».',
'- Игровые меню пока доступны как read-only предпросмотр: `css_vipguns`, `css_wintershop`. Доменный `Buy()` сам не выдаёт оружие.','']
for tier in (1,2,3):
 label,finish,cycle=FINISHES[tier]
 md += [f'## VIP {tier} · {label} — 4 предмета','',f'Бесплатно для VIP уровня {tier} и выше; для остальных — {tier*150 if tier<3 else 600} снежинок за предмет на карту. Способности ниже **заданы в конфиге, но ещё не реализованы в CS2**.','']
 for w in (x for x in weapons if x['required_vip']==tier):
  md += [f"### {w['render_name']}",'',f"![{w['render_name']}](../assets/frost_cs2/{w['render']})",'',
  f"- ID: `{w['id']}`. Имя в игровом конфиге: **{w['name']}**.",
  f"- База: `{w['base_weapon']}`; слот: {'основное оружие' if w['slot']=='primary' else 'пистолет'}.",
  f"- Текущий внешний вид: {w['visual_now']}",
  f"- Способность: **{w['ability']}**.",f"- Условие: {w['trigger']}.",f"- Эффект: {w['result']}.",
  f"- Кулдаун: **{w['cooldown']}**. Предусмотренный визуальный эффект способности: {w['visual']}.",'']
md += ['## Переливы и пределы баланса','', '| VIP владельца | Предусмотренный финиш | Цикл |','|---|---|---|']
md += [f'| VIP {t} | {name}: {desc} | {cycle} |' for t,(name,desc,cycle) in FINISHES.items()]
md += ['',
'- Финиш VIP-игрока должен определяться его текущим уровнем, даже на оружии младшей коллекции; для игрока без VIP используется финиш коллекции купленного оружия.',
'- Перелив должен двигаться и на неподвижном оружии, внутри узоров. В Blender создан предварительный мягкий эффект; полноценная реализация в Source 2 ещё впереди.',
'- Способности одинаковы для купленного и бесплатного VIP-варианта.',
'- Базовые значения по проекту — **100 HP / 100 брони**. Максимумы от эффектов — **110 HP / 125 брони**.',
'- Замедления не суммируются. У каждого оружия свой кулдаун. Отдельных реализованных игровых обработчиков этих правил пока нет.','',
'## Ледяные трассеры','', '![Предпросмотр ледяного трассера](../assets/icy_tracers/icy-tracer-preview.png)','',
'- Светлое бело-голубое ядро и голубое свечение, время жизни **0,12 с** с затуханием.',
'- Модуль допускает только зарегистрированный экземпляр нашего оружия: полный handle с serial, владелец/pawn, ID предмета и эпоха карты. Тип оружия или VIP сами по себе не включают эффект.',
'- Начало должно браться из реальной дульной точки этого экземпляра. Без доступной дульной точки эффект пропускается; позиция глаз не подставляется.',
'- Конец определяется по событию попадания; препятствия проверяются серверным ray trace. Нет выдуманной траектории при отсутствии `bullet_impact`.',
'- Поддержаны ограничения дробинок и очередей по данным оружия, защита от повторов, очистка при удалении/выходе/смерти/смене карты и лимит **192 beam-entity**.',
'- Не меняет урон, не подсвечивает врагов. Существующий Weapon Frost Effects должен пропускать свой трассер для этих экземпляров, чтобы не было дублей.',
'- Статус: код и сборка есть, **121 автопроверка прошла**. Реальная регистрация выдачи, дульный resolver и игровой тест ещё нужны.','',
'## Файлы и подтверждение','',
'- `assets/cs2_local/`: 12 GLB, 12 Blender-сцен; исходные OBJ — в `source/`. Эти большие файлы включены в полный архив Git LFS.',
'- `assets/frost_cs2/`: цветовые карты, орнаментальный атлас, 12 рендеров, общий лист и результаты проверки геометрии/UV.',
'- `assets/icy_tracers/`: рендер эффекта и отчёт сборки/проверок.',
'- `src/PegasusVipArsenal/`: доменная политика, read-only каталог и модуль трассеров; `src/PegasusVipArsenal.Contracts/` — общий API.',
'- `config/vip_weapons.concept.json`: все 12 записей, цены, условия и параметры способностей; `config/icy_tracers.json` — внешний вид трассера.',
'- Сборка: **CounterStrikeSharp.API 1.0.378 / .NET 10 / MinimumApiVersion 378**, 0 ошибок и предупреждений.',
'- Проверены все 12 моделей: сохранение геометрии, числа граней и исходных UV, встроенные текстуры GLB и карты 2048×2048.',
'- Прошли 121 проверка трассеров и существующие проверки политики покупок/каталога. Это не игровые тесты CS2.',
'- Полный архив хранится в `archives/PEGASUS_Frost_Arsenal_FULL.zip` через Git LFS; скачивание полного пакета с GitHub и SHA-256 проверены.','',
'## Что требуется для рабочего сервера','',
'1. Подключить роли VIP и существующий баланс снежинок PEGASUS.',
'2. Реализовать единую транзакцию покупки/выдачи/экипировки с откатом.',
'3. Подготовить и скомпилировать Source 2 ресурсы моделей и материалов, подключить нужные игровые риги/анимации.',
'4. Реализовать все 12 способностей и проверки пределов/кулдаунов в игровом движке.',
'5. Подключить применение финиша по VIP владельца, регистрацию экземпляров трассеров и реальные дульные точки, согласовать Weapon Frost Effects.',
'6. Пройти отдельный тест CS2: первое/третье лицо, 32 игрока, смена карты, респавн, отключения, очистка и производительность.','',
'Действующий сервер PEGASUS не изменялся. Весь набор сейчас является проверенным набором 3D-материалов, доменной логики, спецификаций и собранного модуля трассеров, а не завершённой игровой установкой.','']
(ROOT/'docs/WINTER_ARSENAL_OVERVIEW_RU.md').write_text('\n'.join(md))

esc=lambda s:html.escape(str(s),quote=True)
def uri(path,mime):return 'data:'+mime+';base64,'+base64.b64encode((ROOT/path).read_bytes()).decode()
board=uri('assets/frost_cs2/arsenal-cs2.jpg','image/jpeg')
trace=uri('assets/icy_tracers/icy-tracer-preview.png','image/png')
# Keep large image data in native image elements. CSS custom-property values have browser
# size limits; a shared SVG image lets every card crop the same embedded sheet without JS.
status_rows=''.join('<tr>'+''.join('<td>'+esc(c)+'</td>' for c in row)+'</tr>' for row in STATUS)
matrix_rows=''.join('<tr>'+''.join('<td>'+esc(c)+'</td>' for c in row)+'</tr>' for row in MATRIX)
finish_rows=''.join(f'<tr><td>VIP {t}</td><td>{esc(name)}</td><td>{esc(desc)}</td><td>{cycle}</td></tr>' for t,(name,desc,cycle) in FINISHES.items())
cards=[]
for w in weapons:
 idx=w['index']; col=idx//4; row=idx%4
 crop_x=col*960+10; crop_y=240+row*595
 query=' '.join(str(w[k]) for k in ['id','name','render_name','ability']).lower()
 cards.append(f'''<article class="card" data-tier="{w['required_vip']}" data-price="{w['price_snowflakes']}" data-search="{esc(query)}" id="{w['id']}">
<svg class="weapon-image" xmlns="http://www.w3.org/2000/svg" width="940" height="529" viewBox="{crop_x} {crop_y} 940 529" role="img" aria-label="{esc(w['render_name'])}"><title>{esc(w['render_name'])}</title><use href="#arsenal-render-sheet"></use></svg>
<div class="card-body"><div class="eyebrow">КОЛЛЕКЦИЯ VIP {w['required_vip']} · {esc(FINISHES[w['required_vip']][0])}</div>
<h3>{esc(w['render_name'])}</h3><p class="muted">В конфиге: {esc(w['name'])} · ID {w['id']}</p>
<p>{esc(w['visual_now'])}</p><p class="access"></p><p class="muted finish"></p>
<div class="ability"><strong>{esc(w['ability'])}</strong><p><b>Условие:</b> {esc(w['trigger'])}.</p><p>{esc(w['result'])}.</p><p><b>Кулдаун: {esc(w['cooldown'])}</b></p><span class="pending">Способность задана; в CS2 не реализована</span></div>
<p class="muted">Слот: {'основное' if w['slot']=='primary' else 'пистолет'} · цена вне бесплатного доступа: {w['price_snowflakes']} ❄ / карту.</p>
<button type="button" class="zoom" aria-label="Увеличить {esc(w['render_name'])}">Рассмотреть модель</button></div></article>''')
html_template='''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PEGASUS — полный зимний арсенал</title>
<style>
:root{--bg:#07111d;--panel:#101e2e;--text:#e8f3fb;--muted:#a3b7c9;--line:#294054;--cyan:#71dce7;--violet:#bd9aff}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}a{color:var(--cyan)}main{max-width:1440px;margin:auto;padding:34px 24px 70px}nav{display:flex;gap:18px;flex-wrap:wrap;margin:18px 0 30px}nav a{font-size:14px;text-decoration:none}h1{font-size:clamp(32px,5vw,60px);line-height:1.1;letter-spacing:-2px;margin:10px 0 18px}h2{font-size:28px;margin:40px 0 16px}h3{font-size:21px;line-height:1.3;margin:10px 0}p{margin:10px 0}.kicker,.eyebrow{color:var(--cyan);font-size:12px;letter-spacing:1.3px}.muted{color:var(--muted);font-size:14px}.banner{border:1px solid #6a5736;background:#241f1b;padding:18px 22px;border-radius:14px;margin:24px 0}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:25px 0}.stat{padding:20px;background:var(--panel);border:1px solid var(--line);border-radius:14px}.stat strong{display:block;font-size:32px;line-height:1.2;color:var(--cyan)}.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:14px}table{border-collapse:collapse;width:100%;min-width:650px;background:var(--panel)}td,th{text-align:left;padding:16px;vertical-align:top;border-bottom:1px solid var(--line)}th{color:var(--cyan);font-size:13px}tr:last-child td{border-bottom:0}.embedded-assets{position:absolute;width:0;height:0;overflow:hidden;pointer-events:none}.tracer{display:block;width:100%;height:auto;aspect-ratio:2/1;border-radius:14px}.controls{display:flex;gap:14px;flex-wrap:wrap;background:var(--panel);padding:20px;border:1px solid var(--line);border-radius:14px;margin:20px 0}label{display:flex;flex-direction:column;gap:6px;font-size:13px;color:var(--muted)}select,input[type=search]{font:inherit;min-height:42px;background:var(--bg);color:var(--text);border:1px solid #42617a;border-radius:8px;padding:8px 12px}label.check{flex-direction:row;align-items:center;padding-top:20px}input[type=checkbox]{width:20px;height:20px;accent-color:var(--cyan)}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;overflow:hidden}.card[hidden]{display:none}.weapon-image{display:block;width:100%;height:auto;aspect-ratio:940/529;overflow:hidden}.card-body{padding:20px}.ability{border-left:3px solid var(--cyan);padding:10px 14px;background:#091523;border-radius:0 10px 10px 0;margin:18px 0}.ability p{font-size:14px}.pending{font-size:12px;color:#f0c48c}.access{font-size:14px;font-weight:700;color:#a7e8bb}.card[data-free="false"] .access{color:#ffd28e}button,.button{display:inline-block;cursor:pointer;border:1px solid #3d677f;border-radius:8px;background:#17364a;color:var(--text);padding:10px 16px;font:inherit;text-decoration:none}.actions{display:flex;gap:14px;flex-wrap:wrap;margin:20px 0}.note{padding:22px;border:1px solid var(--line);border-radius:14px;margin-top:20px}.two-col{display:grid;grid-template-columns:1fr 1fr;gap:20px}li{margin:8px 0}dialog{max-width:min(1050px,95vw);width:95vw;padding:22px;background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:18px}dialog::backdrop{background:#000b}.close{float:right}dialog .weapon-image{clear:both;margin-top:20px}footer{color:var(--muted);font-size:13px;margin-top:45px}code{font-size:13px;color:#b5ddea}@media(max-width:1100px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:700px){.grid,.two-col{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}main{padding:22px 14px}td,th{padding:12px}h1{letter-spacing:-1px}}@media print{body{background:#fff;color:#111}nav,.controls,.actions,button,dialog{display:none!important}.grid{display:block}.card{break-inside:avoid;margin-bottom:20px}.card,.stat,table,.ability,.banner{background:#fff;color:#111}.muted{color:#444}.grid .card[hidden]{display:block}h2{break-after:avoid}a{color:#111}}
</style></head><body><svg class="embedded-assets" xmlns="http://www.w3.org/2000/svg" width="0" height="0" aria-hidden="true" focusable="false"><defs><image id="arsenal-render-sheet" width="2880" height="2710" href="__BOARD__"></image></defs></svg><main><header><div class="kicker">PEGASUS / WINTER ARSENAL / ПОЛНЫЙ ОБЗОР</div><h1>12 зимних оружий.<br>Три уровня VIP.</h1><p>Модели, привилегии, магазин, суперспособности и ледяные трассеры — в одном автономном отчёте.</p><nav><a href="#status">Что создано</a><a href="#vip">VIP и магазин</a><a href="#arsenal">Все 12 оружий</a><a href="#finishes">Переливы</a><a href="#tracers">Трассеры</a><a href="#next">Что осталось</a></nav></header>
<div class="banner"><strong>Текущий статус: предпросмотр и собранные компоненты.</strong> Модели и текстуры созданы, модуль трассеров собран. Выдача и применение скинов, роли/баланс PEGASUS ещё не интегрированы; все 12 способностей пока являются спецификацией. В CS2 набор не проверен.</div>
<div class="stats"><div class="stat"><strong>12</strong>GLB и Blender-сцен</div><div class="stat"><strong>3</strong>VIP-коллекции</div><div class="stat"><strong>121</strong>проверка трассеров</div><div class="stat"><strong>0</strong>игровых тестов CS2</div></div>
<div class="actions"><a class="button" href="__ARCHIVE__">Полный пакет в GitHub</a><a class="button" href="__PR__">Исходники · PR #2</a><button type="button" id="print">Печать / PDF</button></div>
<section id="status"><h2>Что действительно создано</h2><div class="table-wrap"><table><thead><tr><th>Блок</th><th>Результат</th><th>Ограничения</th></tr></thead><tbody>__STATUS__</tbody></table></div></section>
<section id="vip"><h2>VIP и покупка за снежинки</h2><p>Матрица ниже реализована в доменной логике. Подключение к настоящим ролям и кошельку PEGASUS ещё требуется.</p><div class="table-wrap"><table><thead><tr><th>Игрок</th><th>Бесплатно, шт.</th><th>Доступ по правилам</th><th>Остальное</th></tr></thead><tbody>__MATRIX__</tbody></table></div><div class="two-col"><div class="note"><strong>Покупка на одну карту</strong><p>Все 12 доступны обычным игрокам: I — 150 ❄, II — 300 ❄, III — 600 ❄ за предмет. Цены предварительные.</p><p>Смерть, респавн и переподключение не отменяют купленный доступ. Повторное «Взять» бесплатно. При смене карты сбрасываются покупки, но не баланс.</p></div><div class="note"><strong>Выдача по проекту</strong><p>Первая покупка и VIP «Взять» должны сразу выдать и экипировать оружие в текущей жизни, с откатом при ошибке. Эта транзакция ещё не реализована.</p><p>Используется существующая экономика PEGASUS. Команды каталога и магазина пока работают как read-only предпросмотр.</p></div></div></section>
<section id="arsenal"><h2>Арсенал и все суперспособности</h2><p>Имена на моделях — из видеореференса. Прежние имена в конфиге показаны на каждой карточке; связь идёт по неизменному ID. Все перечисленные способности ещё требуют игрового обработчика.</p><div class="controls"><label>Проверить доступ по правилам<select id="role"><option value="0">Обычный игрок</option><option value="1">VIP I</option><option value="2">VIP II</option><option value="3">VIP III</option></select></label><label>Коллекция<select id="collection"><option value="0">Все три коллекции</option><option value="1">VIP I · Иней</option><option value="2">VIP II · Метель</option><option value="3">VIP III · Аврора</option></select></label><label>Поиск<input id="search" type="search" placeholder="Оружие, скин или способность"></label><label class="check"><input id="free" type="checkbox">Только бесплатно по выбранному VIP</label></div><p id="count" class="muted">Показаны все 12 оружий.</p><div class="grid">__CARDS__</div></section>
<section id="finishes"><h2>Финиш зависит от владельца</h2><div class="table-wrap"><table><thead><tr><th>Владелец</th><th>Финиш</th><th>Предусмотренный вид</th><th>Цикл</th></tr></thead><tbody>__FINISHES__</tbody></table></div><p>VIP получает финиш своего уровня и на оружии младшей коллекции. Без VIP используется финиш коллекции купленного предмета. Способности платного и бесплатного вариантов одинаковы.</p><p class="muted">В Blender есть предварительный мягкий перелив. Полные финиши Source 2 и динамическая смена по текущему VIP не реализованы в игре; GLB сохраняет статический материал.</p><div class="note"><strong>Пределы баланса по проекту</strong><p>База 100 HP / 100 брони. Верхние пределы от эффектов: 110 HP / 125 брони. Замедления не суммируются, у каждого оружия отдельный кулдаун. Игровые обработчики этих ограничений ещё нужны.</p></div></section>
<section id="tracers"><h2>Ледяной след только от нашего экземпляра</h2><img class="tracer" src="__TRACE__" width="1600" height="800" alt="Blender-предпросмотр ледяного трассера на модели AK-47"><p>Светлое ядро, голубое свечение, затухание за <strong>0,12 секунды</strong>. Урон и подсветка врагов не добавляются.</p><div class="two-col"><div class="note"><strong>Точная привязка</strong><p>Нужны зарегистрированный экземпляр, полный handle с serial, владелец и pawn текущей жизни, ID предмета и эпоха карты. Обычный AK/Glock и один лишь VIP эффект не включают.</p><p>Начало — реальный muzzle attachment конкретного оружия. Нет дульной точки — эффект пропускается; позиция глаз не подставляется.</p></div><div class="note"><strong>Проверки и очистка</strong><p>Реальная точка попадания, ограничение по препятствиям, дробь/очереди по данным оружия, защита от повторов, очистка и максимум 192 beam-entity. Отдельно исключаются дубли Weapon Frost Effects.</p><p>Сборка API 1.0.378 / .NET 10 и 121 автопроверка прошли. Реальная выдача, дульный resolver и проверка в CS2 ещё требуются.</p></div></div></section>
<section id="next"><h2>Что нужно для рабочего сервера</h2><ol><li>Подключить настоящие VIP-роли и существующий баланс снежинок PEGASUS.</li><li>Реализовать общую транзакцию покупки, выдачи и экипировки с откатом.</li><li>Подготовить Source 2 ресурсы, игровые риги/анимации и скомпилировать материалы/модели.</li><li>Реализовать игровые обработчики всех 12 способностей, лимиты и кулдауны.</li><li>Подключить финиш по владельцу, регистрацию экземпляров трассеров и реальные дульные точки, согласовать внешний Weapon Frost Effects.</li><li>Пройти отдельный тест CS2: первое/третье лицо, 32 игрока, смена карты, респавн, выход, очистка и производительность.</li></ol><p>Большие модели и тестовая DLL доступны в полном архиве Git LFS. Текстуры, исходники и отчёты сохранены отдельными файлами в репозитории. Установленная версия API сервера неизвестна; действующий PEGASUS не изменялся.</p></section>
<footer>Автономный HTML: изображения встроены, внешние библиотеки и запросы для просмотра не нужны. Ссылки на GitHub требуют интернета. Геометрия — официальный пакет Valve CS2 Workshop; новые орнаменты — интерпретация видеореференса. Ни одно изображение здесь не является доказательством игрового теста CS2.</footer>
<dialog id="modal"><button class="close" type="button">Закрыть</button><h3></h3><div id="modal-image"></div><p></p></dialog></main>
<script>
const role=document.getElementById('role'), collection=document.getElementById('collection'), search=document.getElementById('search'), onlyFree=document.getElementById('free');
const cards=[...document.querySelectorAll('.card')];const finishNames={1:'Иней',2:'Метель',3:'Аврора'};
function refresh(){const vip=Number(role.value), tier=Number(collection.value), q=search.value.toLocaleLowerCase().trim();let shown=0;
for(const card of cards){const native=Number(card.dataset.tier),free=vip>=native;card.dataset.free=String(free);card.hidden=(tier!==0&&native!==tier)||(onlyFree.checked&&!free)||(q&&!card.dataset.search.includes(q));if(!card.hidden)shown++;
card.querySelector('.access').textContent=free?'По правилам: бесплатно по VIP':'По правилам: '+card.dataset.price+' снежинок / карту';
const finish=vip>0?vip:native;card.querySelector('.finish').textContent='Предусмотренный финиш: '+finishNames[finish]+(vip>0?' — по VIP владельца':' — родной финиш коллекции');}
document.getElementById('count').textContent='Бесплатно по выбранному уровню: '+cards.filter(c=>vip>=Number(c.dataset.tier)).length+' из 12. Сейчас показано: '+shown+'. Это просмотр правил, не игровая покупка.';}
for(const el of [role,collection,onlyFree])el.addEventListener('change',refresh);search.addEventListener('input',refresh);refresh();
const modal=document.getElementById('modal');for(const button of document.querySelectorAll('.zoom'))button.addEventListener('click',()=>{const card=button.closest('.card');modal.querySelector('h3').textContent=card.querySelector('h3').textContent;document.getElementById('modal-image').replaceChildren(card.querySelector('.weapon-image').cloneNode(true));modal.querySelector('p').textContent=card.querySelector('.muted').textContent+' · Рендер Blender; игровой тест CS2 не выполнен.';modal.showModal();});modal.querySelector('.close').addEventListener('click',()=>modal.close());document.getElementById('print').addEventListener('click',()=>window.print());
</script></body></html>'''
for old,new in [('__BOARD__',board),('__TRACE__',trace),('__STATUS__',status_rows),('__MATRIX__',matrix_rows),('__CARDS__',''.join(cards)),('__FINISHES__',finish_rows),('__ARCHIVE__',ARCHIVE),('__PR__',PR)]:html_template=html_template.replace(old,new)
(ROOT/'preview/winter-arsenal-overview.html').write_text(html_template)
print('Created docs/WINTER_ARSENAL_OVERVIEW_RU.md and preview/winter-arsenal-overview.html')
print('HTML bytes:',len(html_template.encode()))
