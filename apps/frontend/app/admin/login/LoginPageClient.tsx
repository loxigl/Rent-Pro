"use client";

import {useEffect} from 'react';
import {useRouter} from 'next/navigation';
import LoginForm from '@/components/admin/auth/LoginForm';

export default function LoginPageClient() {
    const router = useRouter();

    useEffect(() => {
        const accessToken = localStorage.getItem('accessToken');
        const refreshToken = localStorage.getItem('refreshToken');

        if (accessToken && refreshToken) {
            router.push('/admin');
        }
    }, [router]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-primary-700">Kvartiry26</h1>
                    <p className="text-gray-600 mt-2">Административная панель управления</p>
                </div>

                <LoginForm onSuccess={() => router.push('/admin')}/>
            </div>
        </div>
    );
}
