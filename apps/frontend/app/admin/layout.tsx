"use client";

import {ReactNode} from 'react';
import {usePathname} from 'next/navigation';
import AdminHeader from '@/components/admin/layout/AdminHeader';
import AdminSidebar from '@/components/admin/layout/AdminSidebar';
import ProtectedRoute from '@/components/admin/auth/ProtectedRoute';
import {ToastProvider} from "@/components/ui/use-toast";

interface AdminLayoutProps {
    children: ReactNode;
}

export default function AdminLayout({children}: AdminLayoutProps) {
    const pathname = usePathname();
    const isLoginPage = pathname === '/admin/login';

    // Если это страница логина, не показываем шапку и сайдбар
    if (isLoginPage) {
        return (
            <ToastProvider>
                {children}
            </ToastProvider>
        );
    }

    return (
        <ProtectedRoute>
            <ToastProvider>
                <div className="min-h-screen bg-gray-100">
                    <AdminHeader/>
                    <div className="flex">
                        <AdminSidebar/>
                        <main className="flex-1 p-4 md:p-6 max-w-full">
                            {children}
                        </main>
                    </div>
                </div>
            </ToastProvider>
        </ProtectedRoute>
    );
}