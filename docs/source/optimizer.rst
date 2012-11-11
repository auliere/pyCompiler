Оптимізатор коду на асемблері
======================================

.. automodule:: pyCompiler.utils.optimizer

.. py:currentmodule:: pyCompiler.utils.optimizer
.. py:function:: optimize(pseudo)
	Функція, відповідальна за оптимізацію

	:param pseudo: список операторів псевдо-асемблерного коду
	:rtype: оптимізований список операторів псевдо-асемблерного коду

Оптимізація проводиться в кілька ітерацій, за замовчуванням код подходить оптимізатори два рази.

Оптимізатори - функції, які оптимізують кожна свою конструкцію.

Оптимізатор роботи зі стеком
--------------------------------------

.. py:currentmodule:: pyCompiler.utils.optimizer
.. py:function:: optimize_push_pop(pseudo)

Видаляє конструкції виду::

	push eax
	pop eax

Такі конструкції з'являються після генерації коду.

Оптимізатор подвійного копіювання
--------------------------------------

.. py:currentmodule:: pyCompiler.utils.optimizer
.. py:function:: optimize_mov(pseudo)

Оптимізує конструкції вигляду::

	mov eax, 5
	mov ebx, eax

у::

	mov ebx, 5

Такі конструкції з'являються після генерації коду.

Оптимізатор подвійного копіювання для стеку
--------------------------------------

.. py:currentmodule:: pyCompiler.utils.optimizer
.. py:function:: optimize_mov_push(pseudo)

Оптимізує конструкції вигляду::

	mov eax, 5
	push eax

у::

	push dword 5

Такі конструкції з'являються після генерації коду.

Оптимізатор копіювання самого в себе
--------------------------------------

.. py:currentmodule:: pyCompiler.utils.optimizer
.. py:function:: optimize_mov_to_self(pseudo)

Видаляє строки вигляду::

	mov eax,eax

Такі конструкції з'являються внаслідок роботи інших оптимізацій.