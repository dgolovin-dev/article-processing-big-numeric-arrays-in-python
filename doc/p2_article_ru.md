# Как быстро и удобно ворочать большими массивами в python (часть 2)
В первой части статьи я говорил о том, как правильно хранить и загружать большие объемы числовых данных.

В этой части статьи поговорим о технический аспектах вычислений.

Напомню, что в конце предыдущей статьи мы остановились на том, что загрузили весь массив числовых данных в xarray.DataArray.

Переходим к вычислениям.

## Задача
Напоминаю формулировку задачи (чтоб не бегать по ссылкам).

Нужно рассчитать распределение весов акций в портфеле для каждого дня, если разрешено покупать акции только с положительным ema(20) от close, а соотношение весов должно соответствовать соотношению ema(30) от ликвидности (close*volume).

EMA - экспоненциальное скользящее среднее.

Ограничения: расчеты должны занимать менее 10 секунд и потреблять менее 1.5 GB памяти.

Обращайте внимание только на технические аспекты, статья об этом.

## Реализуем вычисления

###Первый блин
Что надо, EMA рассчитать? Да не вопрос, сразу пишем код:

[Example #1. Code](../src/p2_e1_calc_ema.py)
```python
from p1_e4_load_xr_netcdf import data
import xarray as xr
import numpy as np

def calc_ema(data, n):
    k = 2.0 / (1 + n)
    _k = 1 - k
    ema = xr.DataArray(
        np.zeros([len(data.coords['asset']), len(data.coords['date'])], np.float64),
        dims=['asset', 'date'],
        coords={'date': data.coords['date'], 'asset': data.coords['asset']}
    )
    for a in data.coords['asset']:
        pe = np.nan
        for t in data.coords['date']:
            e = data.loc[a, t]
            if not np.isnan(pe):
                if np.isnan(e):
                    e = pe
                else:
                    e = k * e + _k * pe
            ema.loc[a, t] = e
            pe = e
    return ema

if __name__ == '__main__':
    ema = calc_ema(data.loc[:, 'close', :], 20)
    print('done')
``` 

Запускаем и смотрим что получилось… 

[Example #1. Run](../src/p2_e1_run.sh)
```bash
#!/usr/bin/env bash

echo "Part #2 example #1: calc ema"
/usr/bin/time -f "%E %MKb" python3 p2_e1_calc_ema.py > ../report/p2_e1.txt 2>&1
``` 

[Example #1. Report](../report/p2_e1.txt)
```
loaded
[648.75]
Traceback (most recent call last):
...
KeyboardInterrupt
Command exited with non-zero status 1
9:00.91 1242328Kb
```

И не можем дождаться результата. Вычисления займут около 2 часов. Едрен батон!

Что мы сделали не так? Обычные циклы, память вроде не выделяем… Вот именно, что обычные циклы! Обработка данных напрямую в python по одному элементу из DataArray (или ndarray) довольно долгая штука. Сам доступ к одному элементу xarray долгий (однако если бы был “pure python”, все равно бы сильно тормозило, хоть и поменьше). Надо убирать эти python циклы и уменьшать количество операций с xarray.
###Групповые операции
Погружаемся в доку по ndarray и xarray и узнаем, что вообще-то с такими массивами принято работать не по одному элементу, а сразу с группой элементов. Т.е. можно считывать, вести расчеты, и записывать сразу целыми срезами. Ок, смотрим на наш алгоритм и думаем как его можно модифицировать. По идее, если работать сразу со всеми ассетами за день, как с вектором (одномерным массивом), можно убрать один внутренний цикл. Нам очень повезло, что данные уложены в многомерный массив и можно делать соответствующие срезы (на самом деле - нет - так сделано умышленно). Модифицируем алгоритм и посмотрим что получилось:

[Example #2. Code](../src/p2_e2_calc_ema_slice.py) 
```python
from p1_e4_load_xr_netcdf import data
import xarray as xr
import numpy as np

def calc_ema(data, n):
    k = 2.0 / (1 + n)
    _k = 1 - k
    ema = xr.DataArray(
        np.zeros([len(data.coords['asset']), len(data.coords['date'])], np.float64),
        dims=['asset', 'date'],
        coords={'date': data.coords['date'], 'asset': data.coords['asset']}
    )
    prev_ema = xr.DataArray(
        np.full([len(data.coords['asset'])], np.nan, dtype=np.float64),
        dims=['asset'],
        coords={'asset': data.coords['asset']}
    )
    for t in data.coords['date']:
        cur_data = data.loc[:, t]
        cur_finite = np.isfinite(cur_data)
        prev_finite = np.isfinite(prev_ema)

        ema.loc[:, t] = cur_data
        ema.loc[prev_finite, t] = prev_ema.loc[prev_finite]
        cur_prev_finite = np.logical_and(prev_finite, cur_finite)
        ema.loc[cur_prev_finite, t] = (k * cur_data + _k * prev_ema).loc[cur_prev_finite]

        prev_ema = ema.loc[:, t]
    return ema

if __name__ == '__main__':
    ema = calc_ema(data.loc[:, 'close', :], 20)
    print('done')
```

Запускаем:

[Example #2. Run](../src/p2_e2_run.sh)
```bash
#!/usr/bin/env bash

echo "Part #2 example #2: calc ema slice"
/usr/bin/time -f "%E %MKb" python3 p2_e2_calc_ema_slice.py > ../report/p2_e2.txt 2>&1
```

[Example #2. Report](../report/p2_e2.txt)
```
loaded
[648.73828125]
done
0:52.66 1242228Kb
```

Заняло меньше минуты. Это лучше, чем 2 часа, но все равно много, надо думать как сделать быстрее. Если бы я это писал на С, то это бы отработало за секунду. Хм, С… Есть идеи.

###На дне
Вот несколько вариантов ускорить эти вычисления реализовав их на более низком уровне:

Реализовать свою библиотеку на С и подключить к python (слишком сложно)
Реализовать функцию на cython, но это тоже слишком сложно, хоть и проще чем 1.
Использовать JIT компиляцию в Numba (с большой Буквы =) ), наш вариант!
Первые два варианта требуют знания другого языка (cython - это уже не совсем python) и еще надо возиться с компиляцией и подключением этих модулей. Это все сложно и не нужно, когда тот же профит может дать Numba c гораздо меньшими сложностями. C Numba вам не придется учить новый язык, но все-таки придется ограничить типы входных/выходных данных (базовые числовые типы и ndarray), а компиляция вашего кода произойдет в рантайме без вашего участия. Ну хватит сотрясать воздух, давай модифицируем первую реализацию ema для Numba:

[Example #3. Code](../src/p2_e3_calc_ema_numba.py) 
```python
from p1_e4_load_xr_netcdf import data
import xarray as xr
import numpy as np
from numba import jit

@jit
def numba_ema(data, n):
    k = 2.0 / (1 + n)
    _k = 1 - k
    ema = np.zeros(data.shape, np.float64)
    for a in range(data.shape[0]):
        pe = np.nan
        for t in range(data.shape[1]):
            e = data[a, t]
            if not np.isnan(pe):
                if np.isnan(e):
                    e = pe
                else:
                    e = k * e + _k * pe
            ema[a, t] = e
            pe = e
    return ema


def calc_ema(data, n):
    nparr = data.values
    nparr = numba_ema(nparr, n)
    return xr.DataArray(nparr, dims=['asset', 'date'], coords={'date': data.coords['date'], 'asset': data.coords['asset']})

if __name__ == '__main__':
    ema = calc_ema(data.loc[:, 'close', :], 20)
    print('done')
```

И пробуем запустить:

[Example #3. Run](../src/p2_e3_run.sh) 
```bash
#!/usr/bin/env bash

echo "Part #2 example #3: calc ema numba"
/usr/bin/time -f "%E %MKb" python3 p2_e3_calc_ema_numba.py > ../report/p2_e3.txt 2>&1
```

[Example #3. Report](../report/p2_e3.txt)
```
loaded
[648.99609375]
done
0:01.04 1242504Kb
```

Если учитывать, что загрузка данных заняла около секунды, то сами вычисления шли тоже не более 1 секунды. Теперь это приемлемо.

Дайте немного объясню магию Numba. Декоратор @jit при первом запуске функции превратит наш python код в машинный, а тот уже выполняется гораздо быстрее.

С ограничениями типов (ndarray) придется смириться. В остальных 2 случаях пришлось бы тоже понижать уровень абстракции и c этим ничего не поделать. Просто страдай смирись.

С другими вариантами типа cython или C можно добиться сходного результата, но повозиться придется сильно больше (я отвечаю за свои слова).

###Конец близок
Ну и закончим наши вычисления написав алгоритм составления портфеля, используя операции c группами элементов (учтем предыдущий опыт):

[Example #4. Code](../src/p2_e4_final_calc.py)
```python
from p1_e4_load_xr_netcdf import data
from p2_e3_calc_ema_numba import calc_ema
import xarray as xr
import numpy as np

# нужно провести поправку на сплиты перед расчетом ema
split_cumprod = data.loc[:, 'split', :].cumprod('date')
data.loc[:, ['close', 'open', 'high', 'low', 'divs'], :] = data.loc[:, ['close', 'open', 'high', 'low', 'divs'], :] * split_cumprod
data.loc[:, 'vol', :] = data.loc[:, 'vol', :] / split_cumprod

#собственно расчет портфеля
close_ema = calc_ema(data.loc[:, 'close', :], 20)
liquidity_ema = calc_ema(data.loc[:, 'close', :] * data.loc[:, 'vol', :], 30)
portfolio = liquidity_ema.where(close_ema > 0).fillna(0)

# нормировка
portfolio_daily_sum = portfolio.sum('asset')
portfolio_daily_sum = portfolio_daily_sum.where(portfolio_daily_sum > 0).fillna(1)
portfolio = portfolio / portfolio_daily_sum

portfolio.to_netcdf('../portfolio.nc', compute=True)
# portfolio.transpose('date', 'asset').to_pandas().to_csv('portfolio.csv')

print("done")
```

И запустим это:

[Example #4. Run](../src/p2_e4_run.sh) 
```bash
#!/usr/bin/env bash

echo "Part #2 example #4: final calc"
/usr/bin/time -f "%E %MKb" python3 p2_e4_final_calc.py > ../report/p2_e4.txt 2>&1
```

[Example #4. report](../report/p2_e4.txt) 
```
loaded
[649.1328125]
done
0:02.18 1618792Kb
```

Итого: программа выполняется менее 3 секунд потребляя в пике не более 1.2GB памяти. Здесь и Numba не нужен. Все, задача решена.

##Итог
Используя операции с группами элементов массива и используя JIT из Numba (там, где это необходимо), мы произвели расчет всего за 2 секунды.

##Выводы
Думайте об организации данных в ОЗУ, правильно подобранные структуры данных позволяют не только сэкономить память, но и ускорить вычисления в дальнейшем.

1. Используйте специальные библиотеки (numpy, pandas, xarray).

2. Используйте операции над группами элементов. Приведенные выше библиотеки поддерживают операции с группами элементов и делают это очень эффективно. Общее правило, старайтесь уменьшить количество операций, но задействуйте как можно больше элементов в этих операциях.

3. Используйте низкоуровневую оптимизацию там, где это необходимо. С Numba это не так уж и сложно. Но не переборщите с этим =)

##Пока
Всем успехов, все свободны.

Автор статьи — Головин Дмитрий golovin@quantnet.ai

