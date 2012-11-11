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

	function mul(x,y)
	    R = x*y;
	    return R;
	endfunc;

	read j;
	i = 5*mul(j,2);
	print i;
	print "\n";

Генерує такий код на асемблері

.. code-block:: none

	; Source file: e7.src
	; Generated 2012-11-11 15:35:50

	SECTION .data

		_kernel_:	equ	0x80
		; Strings
		numbs:	db		"%d", 0
		numbs_in_format:	db		"%d",0
		; Variables
		vmul_x:		dd	0
		vmul_y:		dd	0
		vmul_R:		dd	0
		vj:		dd	0
		vi:		dd	0

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
		mov	dword	ebp, esp
		
		; Function mul
			jmp	Func1End
			Func_mul:
		
			mov	dword	eax, [esp+4]
			mov	dword	[vmul_x], eax
			mov	dword	eax, [esp+8]
			mov	dword	[vmul_y], eax
			mov	dword	eax, [vmul_x]
			mov	dword	ebx, [vmul_y]
			imul	ebx
		
			ret
			Func1End:
		
		push	dword	vj
		push	dword	numbs_in_format
		call	scanf
		add	esp, 8
		call	getchar
		
		push	dword	2
		push	dword	[vj]
		call	Func_mul
		add	esp, 8
		
		push	dword	eax
		mov	dword	eax, 5
		pop	dword	ebx
		imul	ebx
		
		mov	dword	[vi], eax
		push	dword	[vi]
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
