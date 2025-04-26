import {clsx, type ClassValue} from 'clsx';
import {twMerge} from 'tailwind-merge';

/**
 * Объединяет классы с помощью clsx и twMerge.
 * Позволяет легко комбинировать классы и избегать дублирования
 */
export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}