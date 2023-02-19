# SHA-256

Наколеночная реализация алгоритма хэширования SHA256 на Python. Делалась скорее из исследовательского
интереса, чем ради практической пользы (в конце концов, этот алгоритм уже есть в стандартной библиотеке).

Спасибо за вдохновение этому видео: [How Does SHA-256 Work?](https://www.youtube.com/watch?v=f9EbD6iY9zI)

## Использование
`git clone git@github.com:Klavionik/sha256.git`  
`cd sha256`  
`poetry install`  
`poetry run sha256 <string>`

Чтобы увидеть подробное логирование прогресса хэширования, можно использовать флаг `-d` (`--debug`).

## Тесты
`poetry install`  
`python -m unittest`
