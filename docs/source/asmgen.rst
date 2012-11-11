Генератор коду мови асемблера
======================================

.. automodule:: pyCompiler.utils.gen_asm

Генерує код в синтаксисі nasm на основі псевдо-асемблерні коду.

Перетворює обмежену кількість команд псевдо-асемблера у реальний код. Кожна команда має однозначний еквівалент в компіляторі асемблеру NASM.

.. py:currentmodule:: pyCompiler.utils.gen_asm
.. py:function:: gen_real_asm(pseudo, src_file)
	
	Функція, що відповідає за генерацію кода

	:param pseudo: код на псевдо-асемблері
	:param src_file: назва файлу вихідного коду
	:rtype: код для NASM

.. py:currentmodule:: pyCompiler.utils.gen_asm
.. py:function:: nasm_gen(l)
	
	Перетворення команди на код в синтаксисі NASM

	:param l: команда псевдо-асемблера
	:rtype: команда в синтаксисі NASM

Приклад
------------------------------------------
Код на мові myl::

	function mod(m)
		m = 1;
		return m;
	endfunc;

	read x;
	j = mod(x);
	print x;

Генерує такий код на асемблері

.. code-block:: none

	; Source file: t8.src
	; Generated 2012-11-11 15:00:31

	SECTION .data
		_kernel_:	equ	0x80
		; Strings
		numbs:	db		"%d", 0
		numbs_in_format: db	"%d",0
		; Variables
		vmod_m:		dd	0
		vx:		dd	0
		vj:		dd	0

	SECTION .text
		global	_start
		extern	printf
		extern	scanf
		extern	getchar
		extern	fflush
		extern	stdout
		_start:
		; setup stack frame
		push	dword	ebp
		mov		dword	ebp, esp
		
		; Function mod
			jmp	Func1End
			Func_mod:
			mov	dword	eax, [esp+4]
			mov	dword	[vmod_m], eax
			mov	dword	eax, 1
			ret
			Func1End:
		
		push	dword	vx
		push	dword	numbs_in_format
		call	scanf
		add	esp, 8
		call	getchar
		
		push	dword	[vx]
		call	Func_mod
		add	esp, 4
		
		mov	dword	[vj], eax
		push	dword	[vx]
		push	dword	numbs
		call	printf
		add	esp, 8
		push	dword	[stdout]
		call	fflush
		add	esp, 4
		; restore stack frame
		mov	dword	esp, ebp
		pop	dword	ebp
		mov	dword	ebx, 0
		mov	dword	eax, 1
		int	_kernel_
