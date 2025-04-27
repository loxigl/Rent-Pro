"use client";

import {usePathname} from 'next/navigation';
import Link from 'next/link';

export default function AdminSidebar() {
    const pathname = usePathname();

    const menuItems = [
        {
            name: 'Главная',
            href: '/admin',
            icon: (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path
                        d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
                </svg>
            ),
        },
        {
            name: 'Квартиры',
            href: '/admin/apartments',
            icon: (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path
                        d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"/>
                </svg>
            ),
        },
        {
            name: 'Журнал событий',
            href: '/admin/events',
            icon: (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path
                        fillRule="evenodd"
                        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                        clipRule="evenodd"
                    />
                </svg>
            ),
        },
    ];

    return (
        <aside className="w-64 bg-white shadow-sm h-[calc(100vh-4rem)] sticky top-16 overflow-y-auto hidden md:block">
            <nav className="mt-5 px-2">
                <div className="space-y-1">
                    {menuItems.map((item) => {
                        const isActive =
                            (item.href === '/admin' && pathname === '/admin') ||
                            (item.href !== '/admin' && pathname?.startsWith(item.href));

                        return (
                            <Link
                                key={item.name}
                                href={item.href}
                                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                                    isActive
                                        ? 'bg-primary-50 text-primary-700'
                                        : 'text-gray-700 hover:text-primary-700 hover:bg-gray-50'
                                }`}
                            >
                                <div
                                    className={`mr-3 ${
                                        isActive ? 'text-primary-700' : 'text-gray-500 group-hover:text-primary-600'
                                    }`}
                                >
                                    {item.icon}
                                </div>
                                {item.name}
                            </Link>
                        );
                    })}
                </div>
            </nav>
        </aside>
    );
}