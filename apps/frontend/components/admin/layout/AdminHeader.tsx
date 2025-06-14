"use client";

import React from 'react';
import {Avatar, AvatarFallback} from '@/components/ui/avatar';
import {Button} from '@/components/ui/button';
import Link from 'next/link';
import {useRouter} from 'next/navigation';
import {logoutAdmin} from '@/lib/utils/admin/jwt';

export default function AdminHeader() {
    const router = useRouter();
    const [isDropdownOpen, setIsDropdownOpen] = React.useState(false);

    const handleLogout = async () => {
        try {
            await logoutAdmin();
            router.push('/admin/login');
        } catch (error) {
            console.error('Ошибка при выходе:', error);
        }
    };

    return (
        <header className="bg-white shadow-sm z-10 sticky top-0">
            <div className="px-4 sm:px-6 lg:px-8 h-16 flex justify-between items-center">
                {/* Логотип и заголовок */}
                <div className="flex items-center">
                    <Link href="/admin" className="flex items-center">
                        <h1 className="text-xl font-bold text-primary-700">Kvartiry26</h1>
                        <span className="ml-2 text-xs text-gray-500 px-2 py-1 bg-gray-100 rounded">Admin</span>
                    </Link>
                </div>

                {/* Правая часть шапки с пользовательским меню */}
                <div className="relative">
                    <button
                        className="flex items-center text-gray-700 hover:text-primary-600 focus:outline-none"
                        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    >
                        <div
                            className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-medium">
                            A
                        </div>
                        <span className="ml-2 hidden sm:block">Администратор</span>
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className={`ml-1 h-5 w-5 transform transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`}
                            viewBox="0 0 20 20"
                            fill="currentColor"
                        >
                            <path
                                fillRule="evenodd"
                                d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                                clipRule="evenodd"
                            />
                        </svg>
                    </button>

                    {/* Выпадающее меню */}
                    {isDropdownOpen && (
                        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-20">
                            <Link
                                href="/admin/profile"
                                className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                onClick={() => setIsDropdownOpen(false)}
                            >
                                Профиль
                            </Link>
                            <button
                                onClick={handleLogout}
                                className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            >
                                Выйти
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}