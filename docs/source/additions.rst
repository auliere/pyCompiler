Додатки
====================================

.. [B1] Пустоваров В.И. Ассемблер: программирование и анализ корректности машинных программ. – К: BHV, 2000, Стор. 230-265. 
.. [B2] Dandamudi, S.P.: Guide to Assembly Language Programming in Linux - Springer, 2005,  Стор. 552.
.. [B3] Tanenbaum, A.S. and Woodhull, A.S.: Operating systems: design and implementation - Pearson Prentice Hall, 2006, 1054 c.
.. [B4] Mark Lutz: Learning Python, 2009, 1214 c.
.. [B5] Marty Alchin: Pro Python, 2010, 368 c.
.. [B6] Бек Л.: Введение в системное программирование: Пер. с англ.- М.: Мир, 1988. - 448 с.
.. [B7] Інтернет-ресурс Intel x86 Instruction Reference - http://www.posix.nl/linuxassembly/nasmdochtml/nasmdoca.html
.. [B8] Інтернет-ресурс Running NASM - http://www.nasm.us/doc/nasmdoc2.html

Висновок
--------------------------------------

Було розроблено мову програмування високого рівня, повоної за Тюрингом, до неї розроблено компілятор з функцією оптимізації. Мова описана в формальній граматиці.

Під час написання роботи було написано лексичний, синтаксичний аналізатори, вивчені та реалізовані оптимізаційні алгоритми, робота кінцевого автомату станів, реалізований механізм обробки помилок. Вивчений синтаксис асемблеру NASM, тонкощі компіляції програм для операційної системи GNU/Linux.

Розроблена програма може бути використана як повноцінний компілятор, або бути частиної інтерпретатора з функцію Just-in-Time компіляції, які зараз достатньо поширені. Така можливість істотньо покращить показники швидкості запуску програм інтерпретованих мов програмування.


Код програми
--------------------------------------

./pyc

.. literalinclude:: ../../pyc

./utils/__init__.py

.. literalinclude:: ../../utils/__init__.py

./utils/const.py

.. literalinclude:: ../../utils/const.py

./utils/lexer.py

.. literalinclude:: ../../utils/lexer.py

./utils/syntax.py

.. literalinclude:: ../../utils/syntax.py

./utils/gen.py

.. literalinclude:: ../../utils/gen.py

./utils/optimizer.py

.. literalinclude:: ../../utils/optimizer.py

./utils/gen_asm.py

.. literalinclude:: ../../utils/gen_asm.py